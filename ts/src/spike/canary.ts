import Anthropic from "@anthropic-ai/sdk";
import {appendFileSync, existsSync, mkdirSync, readFileSync, readdirSync, writeFileSync} from "node:fs";
import {join} from "node:path";
import {scaffoldHash} from "./scaffold.ts";
import {REPO_ROOT, classify, loadEnv, runArm, verdictClass, verdictOf, type ArmResult} from "./arms.ts";

/**
 * Gate 7's live D-007 canary.
 *
 * D-007: "pinned transcripts are the CI fixtures; one live canary run executes alongside
 * them, **never fails CI**, and its run history is included in the S2 evidence bundle — an
 * unobserved canary is not evidence."
 *
 * WHAT THE CANARY IS FOR, stated because it is easy to mistake for a test. The suite proves
 * the pipeline contains the injection recorded in July. It cannot say whether the injection
 * still reproduces — every proposal in CI comes from a pinned transcript, and a pinned
 * transcript will keep landing the injection forever, including long after every current
 * model has stopped falling for it. The claim "a real prompt injection changes the agent
 * proposal" would then be true of a recording and false of the world, and nothing in the
 * repository would notice. This is the only thing that would.
 *
 * WHY IT MUST NOT FAIL CI. The model is not under this project's control. A canary wired to
 * fail would make an unrelated vendor change break the build, and the fix under deadline
 * pressure is always to disable the canary — so a failing canary is a canary that gets
 * removed. It reports instead, and the report is what the gate reads.
 *
 * AND WHY A DRIFTED CANARY IS NOT A DEFECT. If today's model resists, that is a finding
 * about the model and a good one; D-007 says so directly ("a negative result is a finding,
 * not a failure"). What it would invalidate is not Sentinel's containment — the pipeline
 * blocks the approval whoever proposed it — but the claim that Case 2's fixture reflects
 * current behaviour. That distinction belongs in the S2 evidence bundle, which is why this
 * writes history rather than a verdict.
 *
 * Run:  npm --prefix ts run canary          (live; needs ANTHROPIC_API_KEY)
 *       npm --prefix ts run canary -- --report   (no API call; prints recorded history)
 */

const INJECTION_DIR = join(REPO_ROOT, "fixtures", "injection");
const HISTORY = join(INJECTION_DIR, "canary-history.jsonl");

interface HistoryRow {
    ranAt: string;
    model: string;
    servedModel: string;
    scaffoldHash: string;
    verdictClass: string;
    verdict: string;
    agreesWithPinned: boolean;
    pinnedFixture: string;
    pinnedVerdictClass: string;
    controlKinds: string[];
    treatmentKinds: string[];
    error?: string;
}

function readHistory(): HistoryRow[] {
    if (!existsSync(HISTORY)) return [];
    return readFileSync(HISTORY, "utf8")
        .split("\n")
        .filter((l) => l.trim() !== "")
        .map((l) => JSON.parse(l) as HistoryRow);
}

/**
 * The pinned recording this run is compared against.
 *
 * Chosen by MODEL rather than by recency, because comparing a live haiku run against a
 * recorded opus run measures the difference between two models and reports it as drift over
 * time. If no recording exists for the model being run, that is stated rather than papered
 * over with the nearest available fixture.
 */
function pinnedFor(model: string): {file: string; verdictClass: string} | null {
    const files = readdirSync(INJECTION_DIR)
        .filter((f) => f.startsWith(`spike-${model}-`) && f.endsWith(".json"))
        .sort();
    const file = files[files.length - 1];
    if (file === undefined) return null;
    const rec = JSON.parse(readFileSync(join(INJECTION_DIR, file), "utf8")) as {verdict: string};
    return {file, verdictClass: verdictClass(rec.verdict)};
}

function report(): void {
    const rows = readHistory();
    console.log("D-007 live canary — recorded run history (Gate 7)");
    if (rows.length === 0) {
        console.log("  NEVER RUN. D-007 requires one live run alongside the pinned transcripts;");
        console.log("  an unobserved canary is not evidence. Run: npm --prefix ts run canary");
        return;
    }
    for (const r of rows.slice(-10)) {
        const agree = r.error !== undefined ? "ERROR " : r.agreesWithPinned ? "agrees" : "DRIFT ";
        console.log(
            `  ${r.ranAt.slice(0, 10)}  ${r.model.padEnd(20)} ${agree}  ${r.verdictClass}` +
                (r.error !== undefined ? `  (${r.error})` : ""),
        );
    }
    const last = rows[rows.length - 1]!;
    const ageDays = Math.floor((Date.parse(new Date().toISOString()) - Date.parse(last.ranAt)) / 86_400_000);
    console.log(`  ${rows.length} run(s) recorded; most recent ${ageDays} day(s) ago.`);
}

// ---------------------------------------------------------------------------

if (process.argv.includes("--report")) {
    report();
    process.exit(0);
}

loadEnv();
const MODEL = process.env.SENTINEL_AGENT_MODEL ?? "claude-haiku-4-5";
const pinned = pinnedFor(MODEL);

const ranAt = new Date().toISOString();
let row: HistoryRow;

try {
    if (pinned === null) {
        throw new Error(`no pinned recording exists for ${MODEL}; nothing to compare against`);
    }
    const client = new Anthropic();
    console.log(`D-007 canary — live run\nmodel: ${MODEL}\nscaffold: ${scaffoldHash()}`);
    console.log(`pinned: ${pinned.file} (${pinned.verdictClass})\n`);

    const control: ArmResult = await runArm(client, MODEL, "control");
    const treatment: ArmResult = await runArm(client, MODEL, "treatment");
    const verdict = verdictOf(control, treatment);
    const cls = verdictClass(verdict);

    row = {
        ranAt,
        model: MODEL,
        servedModel: control.servedModel,
        scaffoldHash: scaffoldHash(),
        verdictClass: cls,
        verdict,
        agreesWithPinned: cls === pinned.verdictClass,
        pinnedFixture: pinned.file,
        pinnedVerdictClass: pinned.verdictClass,
        controlKinds: control.proposals.map(classify),
        treatmentKinds: treatment.proposals.map(classify),
    };
    console.log(`VERDICT : ${verdict}`);
    console.log(`PINNED  : ${pinned.verdictClass}`);
    console.log(row.agreesWithPinned ? "AGREES — the fixture still reflects current behaviour" : "DRIFT — see the note in this file's header; this is a finding, not a failure");
} catch (err) {
    // An infrastructure failure — no key, no network, a 4xx — is recorded as an ERROR row
    // and is NOT drift. Silently swallowing it would leave the history looking like a
    // canary that keeps agreeing, which is the worst available outcome for an instrument
    // whose only job is to be observed.
    const message = err instanceof Error ? err.message : String(err);
    row = {
        ranAt,
        model: MODEL,
        servedModel: "",
        scaffoldHash: scaffoldHash(),
        verdictClass: "ERROR",
        verdict: `ERROR — ${message}`,
        agreesWithPinned: false,
        pinnedFixture: pinned?.file ?? "",
        pinnedVerdictClass: pinned?.verdictClass ?? "",
        controlKinds: [],
        treatmentKinds: [],
        error: message.slice(0, 200),
    };
    console.log(`ERROR: ${message}`);
    console.log("Recorded as an ERROR row. The canary never fails CI (D-007).");
}

mkdirSync(INJECTION_DIR, {recursive: true});
if (!existsSync(HISTORY)) writeFileSync(HISTORY, "");
appendFileSync(HISTORY, JSON.stringify(row) + "\n");
console.log(`\nappended to ${HISTORY.replace(REPO_ROOT, ".")}`);

// Always zero. D-007: "never fails CI".
process.exit(0);
