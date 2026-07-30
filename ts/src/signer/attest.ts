import {domainSeparator, hashAction, hashCallData, hashMandate, hashPolicy, hashUtf8} from "./eip712.ts";
import {decodeBySelector} from "../decode/index.ts";
import type {Keystore} from "./keystore.ts";
import type {ChainReader, VaultState} from "./vault.ts";
import {
    canonicalReasonCodes,
    refusesVerdict,
    severityOf,
    verdictNumber,
    type DecisionReceiptPayload,
    type EvaluateAndSignRequest,
    type EvaluateAndSignResult,
    type Refusal,
    type Hex,
    type ReasonCode,
    type RefusalRecord,
} from "./protocol.ts";

/**
 * The isolated signer's independent checks (§3.1, A-005).
 *
 * WHAT THIS IS, AND — more importantly — WHAT IT IS NOT.
 *
 * §3.1: the signer "independently recomputes the canonical action hash, checks the current
 * mandate and policy, confirms an allow verdict, and signs only the defined receipt
 * payload." Every clause of that is implemented below, and the boundary of the fourth
 * clause is where honesty is easiest to lose.
 *
 * The signer CONFIRMS a verdict. It does not COMPUTE one. It never decodes calldata
 * parameters, never simulates, never inspects effects — those are the decoders (§9 step 4)
 * and the conformance evaluator (§9 step 6), and duplicating them here would produce a
 * second evaluator wearing a signer's name. What the signer independently establishes is
 * that the receipt is *bound* to a real, current, well-formed action under the vault's
 * actual state, read from the chain by the signer itself.
 *
 * The coverage boundary that follows, stated plainly because house rule 4 requires it and
 * because it is the sentence a reader will otherwise supply wrongly for themselves:
 *
 *     This signer prevents a MIS-BOUND receipt from being signed.
 *     It does not prevent a WRONG VERDICT from being signed.
 *
 * If the evaluator concludes ALLOW on an action that conforms to every check the signer
 * can perform but violates the mandate's *purpose* — Case 3, the wrong-resource purchase —
 * the signer will sign it. That is not a gap being excused; it is the division of labour
 * the architecture chose, and it is exactly why §7's harness and the independently
 * labelled corpus, not this file, are what make the verdicts trustworthy.
 *
 * The three severity tiers that govern refusal are documented in `protocol.ts`, next to
 * the reason codes themselves.
 */

/** §5 payloads carry a schemaVersion; v0.2 is 1 throughout, matching the Solidity suite. */
export const RECEIPT_SCHEMA_VERSION = 1n;

const DEFAULT_TTL_SECONDS = 300n;
const MAX_TTL_SECONDS = 3600n;

/** §4: v0.2 supports one top-level operation, CALL, which is Operation enum value 0. */
const OPERATION_CALL = 0n;

export interface AttestorConfig {
    chainId: bigint;
    vault: Hex;
    keystore: Keystore;
    chain: ChainReader;
    defaultTtlSeconds?: bigint;
    maxTtlSeconds?: bigint;
    /** Injectable clock, seconds since epoch. Tests drive expiry deterministically. */
    now?: () => bigint;
    /** Injectable 32-byte source for decisionId. Tests pin it; production uses crypto. */
    randomBytes32?: () => Hex;
}

export interface Attestor {
    evaluateAndSign(request: EvaluateAndSignRequest): Promise<EvaluateAndSignResult>;
    /** Vault state as the signer currently sees it, for `status`. Throws if unreadable. */
    probe(): Promise<VaultState>;
}

/**
 * Per-process, best-effort: at most one live executable attestation per (chain, vault, nonce).
 *
 * THE WORDING IS PART OF THE RULING (D-013). This is defence in depth, NOT a durable system
 * guarantee, and it must never be described as one. The guard lives in this process's memory:
 * a restart forgets it, and two signers sharing a key cannot see each other. "Sentinel
 * guarantees one live attestation per nonce" would be false after a restart, which is the
 * shape of overclaim §7.5 exists to stop. **The vault's nonce is the actual guarantee.** A
 * durable version needs single-writer persistent state before the claim may be strengthened.
 *
 * WHY THIS EXISTS. The vault consumes a nonce on execution, which makes any single
 * credential single-use (§3.3(9)). It does not stop the signer from issuing *two different*
 * ALLOW receipts for the same nonce before either executes — action A and action B, both
 * valid, both live. Whoever relays first wins, and the owner authorised only one of them.
 * The vault cannot detect this; from its side, both are perfectly formed credentials for
 * the current nonce. The signer is the only component positioned to refuse.
 *
 * Re-signing the SAME actionHash is permitted and idempotent — a lost response or a retried
 * request must not deadlock the nonce. An expired prior attestation is also superseded,
 * otherwise an abandoned proposal would wedge the vault until the owner intervened.
 *
 * THE RESERVATION IS SCOPED TO THE AUTHORISATION BASIS, and that narrowing was earned.
 * §4.2 Case 4 ends: "Execution requires a separately signed exact-action owner override
 * **or a new mandate**." The first version reserved on (chain, vault, nonce) alone, so a
 * REVIEW receipt the owner declined to override went on holding the nonce for its whole
 * TTL — and the corrected action taken under a NEW mandate, Case 4's second remedy, was
 * refused until it expired.
 *
 * The reservation therefore records the active mandate and policy hashes it was taken
 * under, and is void once either changes. Two credentials can never be live under two
 * different active mandate hashes — the vault reverts `MandateNotActive` on the stale one —
 * so this is strictly safe rather than a trade.
 *
 * WHAT WAS TRIED AND REJECTED: exempting REVIEW from reserving at all. It looks reasonable
 * — a REVIEW receipt cannot execute by itself — and it is wrong. `executeWithOverride`
 * makes a REVIEW receipt an executable credential the moment the owner signs an exact-action
 * override, so exempting it would allow a live overridable REVIEW for action A1 and a live
 * ALLOW for action A2 at one nonce simultaneously. The owner would have deliberately chosen
 * A1 while A2 raced it to the vault: exactly the "whoever relays first wins" hazard this
 * guard exists to close, reintroduced through the human-in-the-loop path where it matters
 * most. Written here because the reasoning for the exemption is more attractive than the
 * reasoning against it, and the next person will think of it too.
 *
 * HONEST LIMIT: this lives in process memory. Restarting the signer forgets it, and two
 * signer processes sharing a key would not see each other's attestations. The vault's nonce
 * remains the authoritative single-use guard; this is a second, weaker one that closes a
 * window the vault structurally cannot see. Stated here rather than in a commit message
 * because the next person to run two signers deserves to find this warning first.
 */
interface Reservation {
    actionHash: Hex;
    expiresAt: bigint;
    /** The authorisation basis this reservation was taken under. */
    mandateHash: Hex;
    policyHash: Hex;
}

class NonceAttestationGuard {
    private readonly live = new Map<string, Reservation>();

    private static key(chainId: bigint, vault: Hex, nonce: bigint): string {
        return `${chainId}:${vault}:${nonce}`;
    }

    /**
     * True when an unexpired attestation for a DIFFERENT action, taken under the SAME
     * mandate and policy, already holds this nonce.
     */
    conflicts(
        chainId: bigint,
        vault: Hex,
        nonce: bigint,
        actionHash: Hex,
        now: bigint,
        basis: {mandateHash: Hex; policyHash: Hex},
    ): boolean {
        const held = this.live.get(NonceAttestationGuard.key(chainId, vault, nonce));
        if (held === undefined) return false;
        if (now > held.expiresAt) return false;
        // The owner changed the authorisation basis; the old reservation describes a
        // decision that no longer applies (§4.2 Case 4, "or a new mandate").
        if (held.mandateHash !== basis.mandateHash || held.policyHash !== basis.policyHash) {
            return false;
        }
        return held.actionHash !== actionHash;
    }

    record(
        chainId: bigint,
        vault: Hex,
        nonce: bigint,
        actionHash: Hex,
        expiresAt: bigint,
        basis: {mandateHash: Hex; policyHash: Hex},
    ): void {
        const k = NonceAttestationGuard.key(chainId, vault, nonce);
        const held = this.live.get(k);
        // NEVER SHORTEN AN EXISTING RESERVATION FOR THE SAME ACTION. `ttlSeconds` is a
        // caller field, and an idempotent re-sign with a smaller TTL would otherwise move
        // the reservation's expiry *earlier* than the still-valid receipt already issued —
        // freeing the nonce while a live ALLOW receipt for a different action could then be
        // signed alongside it. Take the later of the two.
        const expiry =
            held !== undefined && held.actionHash === actionHash && held.expiresAt > expiresAt
                ? held.expiresAt
                : expiresAt;
        this.live.set(k, {actionHash, expiresAt: expiry, ...basis});
    }

    /**
     * Undo a reservation, but only if it is still ours.
     *
     * Used when signing throws after the nonce was reserved. The actionHash comparison
     * matters: releasing unconditionally would let a failed request cancel a *different*
     * request's live reservation, turning a signing error into the very double-attestation
     * this guard exists to prevent.
     */
    release(chainId: bigint, vault: Hex, nonce: bigint, actionHash: Hex): void {
        const k = NonceAttestationGuard.key(chainId, vault, nonce);
        if (this.live.get(k)?.actionHash === actionHash) this.live.delete(k);
    }

    prune(now: bigint): void {
        for (const [k, v] of this.live) if (now > v.expiresAt) this.live.delete(k);
    }
}

export function createAttestor(config: AttestorConfig): Attestor {
    const {chainId, vault, keystore, chain} = config;
    const defaultTtl = config.defaultTtlSeconds ?? DEFAULT_TTL_SECONDS;
    const maxTtl = config.maxTtlSeconds ?? MAX_TTL_SECONDS;
    const now = config.now ?? (() => BigInt(Math.floor(Date.now() / 1000)));
    const randomBytes32 =
        config.randomBytes32 ??
        (() => {
            const bytes = new Uint8Array(32);
            globalThis.crypto.getRandomValues(bytes);
            return `0x${Array.from(bytes, (b) => b.toString(16).padStart(2, "0")).join("")}` as Hex;
        });

    const guard = new NonceAttestationGuard();
    const localDomainSeparator = domainSeparator(chainId, vault);

    return {
        async probe(): Promise<VaultState> {
            // A zero-address target and zero selector: `probe` only needs the singleton
            // fields, and the allowlist answers for a nonexistent target are ignored.
            return chain.readVaultState(vault, `0x${"0".repeat(40)}` as Hex, "0x00000000");
        },

        async evaluateAndSign(request: EvaluateAndSignRequest): Promise<EvaluateAndSignResult> {
            const {action, callData, mandate, policy, evaluation} = request;
            const findings: ReasonCode[] = [];
            const at = now();

            // D-012: a refusal must leave a recorded artifact, or "the signer refused" and
            // "the signer was never asked" are indistinguishable and S2 cannot prove the signer
            // ever saw the request. `attributable` is false only when the request is too
            // malformed to name an action honestly — a payload contradicting its own calldata
            // describes no action the signer could say it refused.
            const refuse = async (attributable = true): Promise<EvaluateAndSignResult> => {
                const signerFindings = [...new Set(findings)];
                const reasonCodes = [
                    ...new Set([...evaluation.reasonCodes, ...signerFindings]),
                ].sort();

                let refusalRecord: Refusal["refusalRecord"] = null;
                if (attributable) {
                    const record: RefusalRecord = {
                        schemaVersion: RECEIPT_SCHEMA_VERSION,
                        chainId,
                        vault,
                        actionHash: hashAction(action),
                        evidenceHash: hashUtf8(evaluation.evidenceCanonical),
                        requestedVerdict: evaluation.verdict,
                        reasonCodesHash: hashUtf8(canonicalReasonCodes(reasonCodes)),
                        refusedAt: at,
                        signer: keystore.address,
                    };
                    refusalRecord = {
                        record,
                        signature: await keystore.signRefusal(record),
                        reasonCodes,
                    };
                }

                return {
                    refused: true,
                    blocking: findings
                        .filter((c) => refusesVerdict([c], evaluation.verdict))
                        .map((code) => ({code, severity: severityOf(code)})),
                    signerFindings,
                    requestedVerdict: evaluation.verdict,
                    refusalRecord,
                };
            };

            // --- Structural: no chain access required, and no point in chain access
            //     until these hold. A request naming another vault is not this signer's
            //     business, and one whose payload contradicts its own calldata is not
            //     anybody's.
            if (callData.length < 2 + 8) findings.push("SIGNER_CALLDATA_TOO_SHORT");
            if (hashCallData(callData) !== action.dataHash) findings.push("SIGNER_DATAHASH_MISMATCH");
            if (action.vault !== vault) findings.push("SIGNER_WRONG_VAULT");
            if (action.chainId !== chainId) findings.push("SIGNER_WRONG_CHAIN");
            if (findings.length > 0) return refuse(false);

            const selector = callData.slice(0, 10) as Hex;

            // D-014: the signer decodes the bytes ITSELF and checks that the evidence bundle's
            // decoded-parameters claim matches. Derivation without judgement — the mandate is
            // never consulted here. The effect is that the bundle's parameters become
            // signer-attested rather than evaluator-asserted, so the D-010 verifier can detect
            // a wrong-purpose ALLOW after the fact without the signer becoming a second
            // conformance evaluator (the alternative D-014 explicitly rejected).
            //
            // BOUNDARY: this checks the parameters against the bytes GIVEN THE SELECTOR. It does
            // not check that the selector belongs at the target — that stays with the evaluator.
            findings.push(...checkEvidenceDecoding(callData, evaluation.evidenceCanonical));

            // --- Chain state. An unreadable vault is FATAL, never a default (§3.3(8)).
            let state: VaultState;
            try {
                state = await chain.readVaultState(vault, action.target, selector);
            } catch {
                findings.push("SIGNER_VAULT_UNREACHABLE");
                return await refuse();
            }

            // Live cross-language differential: this TypeScript EIP-712 implementation
            // against the Solidity one, every request. If they ever diverge, every
            // signature this process could produce would be rejected onchain — so the
            // useful failure is here and loud, not there and mysterious.
            if (state.domainSeparator !== localDomainSeparator) {
                findings.push("SIGNER_DOMAIN_SEPARATOR_MISMATCH");
                return await refuse();
            }

            const actionHash = hashAction(action);

            // --- EXECUTABILITY: refuses ALLOW and REVIEW, permits BLOCK.
            if (state.signer !== keystore.address) findings.push("SIGNER_NOT_ACTIVE_SIGNER");
            if (action.actionNonce !== state.actionNonce) findings.push("SIGNER_NONCE_MISMATCH");
            if (state.paused) findings.push("SIGNER_VAULT_PAUSED");
            if (at > action.deadline) findings.push("SIGNER_ACTION_EXPIRED");

            // The receipt records the block a verdict was computed against (§5.4). Checking
            // that the block actually has that hash is what keeps "conformance against
            // simulated effects at a recorded block" from being a claim the evaluator can
            // simply assert.
            const simHash = await chain.blockHashAt(evaluation.simulationBlockNumber);
            if (simHash === null || simHash !== evaluation.simulationBlockHash) {
                findings.push("SIGNER_SIMULATION_BLOCK_MISMATCH");
            }

            // The basis is the vault's CURRENT active hashes, not the action's claimed ones:
            // a stale action must not be able to match a reservation by naming the mandate
            // that reservation was taken under.
            const basis = {
                mandateHash: state.activeMandateHash,
                policyHash: state.activePolicyHash,
            };

            guard.prune(at);
            if (guard.conflicts(chainId, vault, action.actionNonce, actionHash, at, basis)) {
                findings.push("SIGNER_NONCE_ALREADY_ATTESTED");
            }

            // --- CONFORMANCE: refuses ALLOW, permits REVIEW (Case 4 lives here).
            const mandateActive = hashMandate(mandate) === state.activeMandateHash;
            const policyActive = hashPolicy(policy) === state.activePolicyHash;
            if (!mandateActive) findings.push("SIGNER_MANDATE_NOT_ACTIVE");
            if (!policyActive) findings.push("SIGNER_POLICY_NOT_ACTIVE");
            if (
                action.mandateHash !== state.activeMandateHash ||
                action.policyHash !== state.activePolicyHash
            ) {
                findings.push("SIGNER_ACTION_BINDING_STALE");
            }

            // Mandate contents are only meaningful once the mandate is known to be the
            // active one. Checking a mandate the vault has not activated would be checking
            // an assertion against itself.
            if (mandateActive) {
                if (mandate.vault !== action.vault || mandate.chainId !== action.chainId) {
                    findings.push("SIGNER_MANDATE_SCOPE_MISMATCH");
                }
                if (mandate.target !== action.target) findings.push("SIGNER_MANDATE_TARGET_MISMATCH");
                if (mandate.selector !== selector) findings.push("SIGNER_MANDATE_SELECTOR_MISMATCH");
                if (action.valueWei > mandate.maxNativeValueWei) {
                    findings.push("SIGNER_MANDATE_VALUE_EXCEEDED");
                }
                if (at < mandate.validAfter || at > mandate.validUntil) {
                    findings.push("SIGNER_MANDATE_WINDOW");
                }
                if (mandate.principal !== state.owner) {
                    findings.push("SIGNER_MANDATE_PRINCIPAL_MISMATCH");
                }
                if (mandate.policyHash !== action.policyHash) {
                    findings.push("SIGNER_MANDATE_POLICY_LINK_MISMATCH");
                }
                if (mandate.targetCodeHash !== state.targetCodeHash) {
                    findings.push("SIGNER_TARGET_CODEHASH_MISMATCH");
                }
            }

            if (policyActive) {
                if (policy.vault !== action.vault || policy.chainId !== action.chainId) {
                    findings.push("SIGNER_POLICY_SCOPE_MISMATCH");
                }
                if (policy.allowedOperation !== action.operation) {
                    findings.push("SIGNER_POLICY_OPERATION_MISMATCH");
                }
                if (action.valueWei > policy.maxNativeValueWei) {
                    findings.push("SIGNER_POLICY_VALUE_EXCEEDED");
                }
                if (at < policy.validAfter || at > policy.validUntil) {
                    findings.push("SIGNER_POLICY_WINDOW");
                }
            }

            if (action.operation !== OPERATION_CALL) findings.push("SIGNER_UNSUPPORTED_OPERATION");

            // The vault's own hard backstops, re-checked here. These are duplicates of
            // checks the vault performs at execution time and they add no enforcement — the
            // vault is and remains the enforcement point. Their value is that a signed
            // ALLOW the vault then rejects becomes a detectable disagreement between the
            // two, rather than a puzzling revert in a demo.
            if (action.valueWei > state.maxNativeValueWei) {
                findings.push("SIGNER_VAULT_VALUE_CAP_EXCEEDED");
            }
            if (!state.targetAllowed) findings.push("SIGNER_VAULT_TARGET_NOT_ALLOWED");
            if (!state.selectorAllowed) findings.push("SIGNER_VAULT_SELECTOR_NOT_ALLOWED");

            if (refusesVerdict(findings, evaluation.verdict)) return await refuse();

            // --- Attest.
            //
            // The signer refuses; it never downgrades. If the evaluator asked for ALLOW and
            // the checks fail, the answer is a refusal, not a BLOCK receipt. Those are
            // different claims — "Sentinel evaluated this action and blocked it" versus "the
            // signer declined to attest" — and an evidence bundle that conflates them
            // misreports what the system concluded.
            const signerFindings = [...new Set(findings)];
            const reasonCodes = [...new Set([...evaluation.reasonCodes, ...signerFindings])].sort();

            const ttl = min(request.ttlSeconds ?? defaultTtl, maxTtl);
            const expiresAt = min(at + ttl, action.deadline);

            const receipt: DecisionReceiptPayload = {
                schemaVersion: RECEIPT_SCHEMA_VERSION,
                // Signer-generated, not caller-supplied: one fewer 32-byte field an outside
                // caller controls inside a structure this process signs.
                decisionId: randomBytes32(),
                actionHash,
                mandateHash: action.mandateHash,
                policyHash: action.policyHash,
                verdict: BigInt(verdictNumber(evaluation.verdict)),
                reasonCodesHash: hashUtf8(canonicalReasonCodes(reasonCodes)),
                // Hashed from the full canonical bundle the caller supplied, never accepted
                // as a pre-computed digest. See `protocol.ts` on why that distinction is the
                // difference between a narrow RPC and a generic signing oracle.
                evidenceHash: hashUtf8(evaluation.evidenceCanonical),
                simulationBlockNumber: evaluation.simulationBlockNumber,
                simulationBlockHash: evaluation.simulationBlockHash,
                issuedAt: at,
                expiresAt,
                signer: keystore.address,
            };

            // RESERVE BEFORE SIGNING, not after.
            //
            // `guard.conflicts` was evaluated further up, and signing is asynchronous. If
            // the reservation were taken after the await — the obvious place, and where this
            // was first written — two concurrent requests for DIFFERENT actions at the SAME
            // nonce would both pass the conflict check while neither had recorded yet, and
            // both would be signed. That is exactly the hazard the guard exists to prevent,
            // reintroduced by the ordering.
            //
            // Everything between the conflict check and this line is synchronous, so on
            // Node's single-threaded event loop check-and-reserve is atomic with respect to
            // other requests. That property is load-bearing: an `await` inserted anywhere in
            // that span silently reopens the window.
            // ALLOW and REVIEW both reserve; BLOCK does not. A REVIEW receipt becomes an
            // executable credential once the owner signs an exact-action override, so
            // exempting it would reopen the hazard — see the guard's header for why that
            // exemption is more tempting than it is correct.
            const reserved = evaluation.verdict !== "BLOCK";
            if (reserved) {
                guard.record(chainId, vault, action.actionNonce, actionHash, expiresAt, basis);
            }

            let signature: Hex;
            try {
                signature = await keystore.signReceipt(receipt);
            } catch (err) {
                // A reservation held by a receipt that was never issued would wedge the nonce
                // until it expired.
                if (reserved) guard.release(chainId, vault, action.actionNonce, actionHash);
                throw err;
            }

            return {
                refused: false,
                receipt,
                signature,
                reasonCodes,
                actionHash,
                evidenceHash: receipt.evidenceHash,
                signerFindings,
            };
        },
    };
}

function min(a: bigint, b: bigint): bigint {
    return a < b ? a : b;
}

/**
 * D-014. Does the evidence bundle's decoded-parameters claim match the calldata?
 *
 * Returns findings rather than throwing, so a malformed bundle is a refusal with a named
 * reason instead of a crash. An absent or unparseable claim is refused rather than skipped:
 * an optional attestation is worthless, because a caller wishing to lie would simply omit
 * the field.
 */
function checkEvidenceDecoding(callData: Hex, evidenceCanonical: string): ReasonCode[] {
    let claim: unknown;
    try {
        claim = (JSON.parse(evidenceCanonical) as Record<string, unknown>)
            .decodedSelectorAndParameters;
    } catch {
        return ["SIGNER_EVIDENCE_DECODING_ABSENT"];
    }
    if (typeof claim !== "object" || claim === null) return ["SIGNER_EVIDENCE_DECODING_ABSENT"];

    const claimed = claim as Record<string, unknown>;
    const mine = decodeBySelector(callData);

    // Both sides must agree on WHETHER the bytes decode at all, before agreeing on what to.
    if (claimed.decoded !== (mine.ok ? "true" : "false")) {
        return ["SIGNER_EVIDENCE_DECODING_MISMATCH"];
    }
    if (!mine.ok) return [];

    if (typeof claimed.selector !== "string" || claimed.selector.toLowerCase() !== mine.selector) {
        return ["SIGNER_EVIDENCE_DECODING_MISMATCH"];
    }
    if (claimed.schema !== mine.decoded.schema) return ["SIGNER_EVIDENCE_DECODING_MISMATCH"];

    const params = claimed.parameters;
    if (typeof params !== "object" || params === null) {
        return ["SIGNER_EVIDENCE_DECODING_ABSENT"];
    }
    const p = params as Record<string, unknown>;

    // Field-by-field against the signer's own decoding. The bundle carries decimal strings
    // (the §5.6 schema has no JSON numbers), so comparison is against `.toString()`.
    const expected: Record<string, string | boolean> =
        mine.decoded.schema === "DemoPay.purchase"
            ? {
                  resourceId: mine.decoded.resourceId,
                  beneficiary: mine.decoded.beneficiary,
                  durationSeconds: mine.decoded.durationSeconds.toString(),
                  recurring: mine.decoded.recurring,
              }
            : {spender: mine.decoded.spender, amount: mine.decoded.amount.toString()};

    for (const [key, want] of Object.entries(expected)) {
        const got = p[key];
        const match = typeof want === "boolean" ? got === want : String(got).toLowerCase() === want;
        if (!match) return ["SIGNER_EVIDENCE_DECODING_MISMATCH"];
    }
    return [];
}
