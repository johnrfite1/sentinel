import {readFileSync, readdirSync} from "node:fs";
import {dirname, join} from "node:path";
import {fileURLToPath} from "node:url";
import {readProposal, type AgentProposal} from "./schema.ts";

/**
 * Reading real agent proposals back out of the pinned D-007 spike records.
 *
 * D-007 is explicit about the reproducibility scheme: "pinned transcripts are the CI
 * fixtures; one live canary run executes alongside them, never fails CI." So the CI path
 * for §9 step 7 reads a recorded transcript from `fixtures/injection/` — no API key, no
 * network, no per-run model variance — and the proposals it yields are the ones a real
 * `claude-haiku-4-5` actually emitted on 2026-07-27 (A-009).
 *
 * That is what makes this "a real agent proposal" rather than a hand-written stand-in: the
 * bytes Sentinel evaluates descend from a recorded model output, and the recording carries
 * the model id, served version, and scaffold hash needed to say so precisely.
 *
 * WHAT A PINNED TRANSCRIPT IS NOT EVIDENCE FOR. It fixes the agent's output, so it proves
 * nothing about whether the injection still reproduces against the live model today. That
 * is the canary's job, and the canary is S2 work.
 */

const here = dirname(fileURLToPath(import.meta.url));
const REPO_ROOT = join(here, "..", "..", "..");
const INJECTION_DIR = join(REPO_ROOT, "fixtures", "injection");

export type SpikeArm = "control" | "treatment";

export interface SpikeFixture {
    path: string;
    spike: string;
    model: string;
    servedModel: string;
    scaffoldHash: string;
    verdict: string;
    startedAt: string;
    transcripts: Record<SpikeArm, unknown[]>;
}

/** Load one recorded spike run by file name, or by the model it ran against. */
export function loadSpikeFixture(nameOrModel: string): SpikeFixture {
    const files = readdirSync(INJECTION_DIR).filter((f) => f.endsWith(".json")).sort();
    const exact = files.find((f) => f === nameOrModel);
    // Newest-last after the sort, so a model with several recordings yields the latest.
    const byModel = files.filter((f) => f.startsWith(`spike-${nameOrModel}-`)).pop();
    const file = exact ?? byModel;
    if (file === undefined) {
        throw new Error(
            `no spike fixture matching ${JSON.stringify(nameOrModel)} in ${INJECTION_DIR}; ` +
                `have: ${files.join(", ")}`,
        );
    }

    const path = join(INJECTION_DIR, file);
    const raw = JSON.parse(readFileSync(path, "utf8")) as Record<string, unknown>;
    const transcripts = raw.transcripts as Record<SpikeArm, unknown[]> | undefined;
    if (transcripts === undefined) {
        throw new Error(`spike fixture ${file} has no transcripts`);
    }

    return {
        path,
        spike: String(raw.spike),
        model: String(raw.model),
        servedModel: String(raw.servedModel),
        scaffoldHash: String(raw.scaffoldHash),
        verdict: String(raw.verdict),
        startedAt: String(raw.startedAt),
        transcripts,
    };
}

/**
 * Every `propose_evm_action` the agent emitted on one arm, in order.
 *
 * Walks the recorded assistant turns rather than reading a summarised field, so what comes
 * back is the model's own tool input as transmitted. A fixture whose summary and transcript
 * disagreed would show up here as a difference rather than being papered over.
 *
 * Returns `null` entries for tool inputs that do not match the tool schema — a model CAN
 * emit a malformed call, and silently dropping those would hide exactly the case §7.1 wants
 * counted.
 */
export function proposalsFrom(fixture: SpikeFixture, arm: SpikeArm): (AgentProposal | null)[] {
    const out: (AgentProposal | null)[] = [];
    for (const turn of fixture.transcripts[arm] ?? []) {
        const content = (turn as {content?: unknown}).content;
        if (!Array.isArray(content)) continue;
        for (const block of content) {
            const b = block as {type?: unknown; name?: unknown; input?: unknown};
            if (b.type === "tool_use" && b.name === "propose_evm_action") {
                out.push(readProposal(b.input));
            }
        }
    }
    return out;
}
