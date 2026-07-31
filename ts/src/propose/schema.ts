/**
 * The untrusted proposal shape, and the only way in.
 *
 * Split from `index.ts` so `fixtures.ts` can validate recorded tool inputs without a cycle
 * back through the module that re-exports it.
 */

/**
 * Exactly the `propose_evm_action` tool schema from `spike/scaffold.ts`.
 *
 * Every field is a string because that is what the tool declares and what the model emits.
 * §3.1 classifies all of them as untrusted — "agent-supplied parameter or purpose claims" —
 * so no consumer may assume any is well-formed, sensible, or honest.
 */
export interface AgentProposal {
    target: string;
    value_wei: string;
    function_signature: string;
    args: string[];
    rationale: string;
}

/**
 * Validate the shape of a model-emitted proposal before any field is read.
 *
 * Returns a typed proposal or `null`. Kept separate from transcription because "the model
 * did not emit the tool schema" and "the model emitted a malformed address" are different
 * findings about the agent, and §7.1 would count them as different fixture classes.
 *
 * The checks are deliberately structural rather than coercive: a `value_wei` arriving as
 * the NUMBER 5000000000000000 is refused rather than stringified, because a model that
 * emits a JSON number for a wei amount has already lost precision above 2^53 and the
 * coercion would hide it.
 */
export function readProposal(raw: unknown): AgentProposal | null {
    if (typeof raw !== "object" || raw === null) return null;
    const r = raw as Record<string, unknown>;
    if (typeof r.target !== "string") return null;
    if (typeof r.value_wei !== "string") return null;
    if (typeof r.function_signature !== "string") return null;
    if (typeof r.rationale !== "string") return null;
    if (!Array.isArray(r.args) || !r.args.every((a) => typeof a === "string")) return null;
    return {
        target: r.target,
        value_wei: r.value_wei,
        function_signature: r.function_signature,
        args: r.args as string[],
        rationale: r.rationale,
    };
}
