import type {Hex, MandatePayload, PolicyPayload, ActionPayload} from "../signer/protocol.ts";

/**
 * The §7.1 adversarial fixture corpus — declarative specifications.
 *
 * §7 states the reason this exists in its opening line: "Four demo paths alone cannot prove
 * that the verdicts are not hard-coded." The corpus is the bar the conformance engine is
 * actually measured against, and HANDOFF's verification partition puts that bar OUTSIDE the
 * implementation — the ground-truth labels are authored by agents with no implementation
 * context, under the prompt frozen by D-011(a), and sampled adversarially by John.
 *
 * CRITICAL: NO FIXTURE IN THIS FILE CARRIES A VERDICT. Not a hint, not an expectation, not a
 * comment saying what "should" happen. The `intent` field describes the SCENARIO — what was
 * set up — never its correct outcome. If a future edit adds an `expected` field here, the
 * corpus stops being an independent bar and becomes the implementers' own opinion written
 * twice, which is precisely the failure D-006 and D-011 exist to prevent. HANDOFF kill
 * criterion 3 makes modifying fixtures or labels to make a suite pass an immediate halt.
 *
 * A fixture is a scenario plus the knobs needed to reach it. Everything derivable is
 * derived at run time against a real chain, so the corpus stays readable and the values that
 * matter (nonces, code hashes, block numbers) are never stale literals.
 */

/** The §7.1 classes, verbatim in meaning, as stable slugs. */
export const FIXTURE_CLASSES = [
    "exact-allowed-and-benign-variation",
    "boundary-and-over-limit-native-value",
    "approvals-finite-oversized-unlimited",
    "wrong-resource-beneficiary-duration-recurrence",
    "altered-calldata-after-receipt",
    "wrong-chain-vault-target-mandate-policy",
    "stale-or-reused-action-nonce",
    "expired-mandate-receipt-or-override",
    "invalid-or-rotated-signer",
    "malformed-calldata-or-unknown-selector",
    "runtime-code-change-or-proxy-target",
    "simulation-revert",
    "rpc-simulator-or-context-outage",
    "conflicting-block-state",
    "malicious-retrieved-instructions",
    "unexpected-internal-call",
    "unsupported-multicall-or-delegatecall",
    "owner-override-and-block-behaviour",
    "reentrancy-attempt",
    "evaluator-or-signer-compromise",
] as const;

export type FixtureClass = (typeof FIXTURE_CLASSES)[number];

/** Which deployed contract the action targets. `unknown` is an address Sentinel has no registry entry for. */
export type TargetName = "demoPay" | "demoErc20" | "unknown";

export type CallSpec =
    | {
          kind: "purchase";
          /** `undefined` means "the mandate's own value" — resolved at run time. */
          resource?: Hex | "wrong";
          beneficiary?: Hex | "attacker";
          durationSeconds?: bigint;
          recurring?: boolean;
      }
    | {kind: "approve"; spender: Hex | "attacker"; amount: bigint | "max"}
    | {
          /**
           * Raw calldata, for the classes a well-formed proposal cannot reach.
           *
           * Recorded as a limit in the step-7 coverage boundary: the proposal transcriber
           * emits only exact-width canonical words, so trailing bytes, dirty address bits and
           * non-canonical bools are unreachable from an agent and must be authored here.
           */
          kind: "raw";
          hex: Hex;
      };

/**
 * Environment manipulations. Each maps to a real state change on a real chain or a real
 * degradation of the pipeline — never a stubbed check result.
 */
export interface EnvSpec {
    /** Owner pauses the vault before evaluation (§3.3(2)). */
    pauseVault?: boolean;
    /** Owner rotates the vault's signer to a different key (§3.3(2), §3.3(6)). */
    rotateSigner?: boolean;
    /** Activate a mandate, then activate a DIFFERENT one, leaving the action bound to the stale hash. */
    supersedeMandate?: boolean;
    /** Activate a different policy after binding. */
    supersedePolicy?: boolean;
    /** Consume the action nonce with a prior successful execution, then re-present this action. */
    consumeNonceFirst?: boolean;
    /** Mutate the calldata AFTER the action's dataHash was computed (§3.3(5)). */
    tamperCalldataAfterBinding?: boolean;
    /** Deploy fresh bytecode at the target after the mandate pinned its code hash. */
    changeTargetCode?: boolean;
    /** Withhold the simulation entirely — the §3.3(8) critical-dependency-failure path. */
    simulationUnavailable?: boolean;
    /** Do not fund the vault, so the value transfer reverts on a real chain. */
    starveVault?: boolean;
    /** Advance chain time past the mandate's validUntil. */
    advancePastMandateWindow?: boolean;
    /** Advance chain time past the policy's validUntil. */
    advancePastPolicyWindow?: boolean;
}

export interface FixtureSpec {
    id: string;
    class: FixtureClass;
    /**
     * One line describing WHAT WAS SET UP. Never what the verdict should be.
     *
     * This is the "declared intent" D-011(b) gives the labeller alongside the schemas and
     * invariants. Write it as a scenario description a stranger could act on, not as a hint.
     */
    intent: string;
    target: TargetName;
    call: CallSpec;
    /** `undefined` means the standard conforming value, resolved at run time. */
    valueWei?: bigint;
    mandate?: Partial<MandatePayload>;
    policy?: Partial<PolicyPayload>;
    /** Applied AFTER the action is bound to chain state, to break a binding (§3.3(4), (5)). */
    action?: Partial<ActionPayload>;
    env?: EnvSpec;
    /**
     * Where this scenario's PRIMARY enforcement lives, when it is not the conformance engine.
     *
     * Several §7.1 classes — reentrancy, nonce reuse, receipt replay — are enforced by the
     * vault and are already covered by the Foundry invariant suite. Including them here is
     * still worthwhile, because the engine has a view of them, but claiming the corpus is
     * what proves them would misattribute the evidence. Stating it keeps the ablation's
     * "detection contribution by layer" honest.
     */
    primaryEnforcement?: "vault-foundry-invariants" | "isolated-signer";
}
