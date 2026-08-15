import {existsSync, readFileSync, writeFileSync} from "node:fs";
import {join} from "node:path";
import {LAYERS, LAYER_DESCRIPTIONS, type LayerName} from "./layers.ts";

/**
 * §7.3 — the security ablation report.
 *
 * D-009 made this a Gate S2 pass condition, and gave the reason: §7 opens by stating that
 * four demo paths cannot prove the verdicts are not hard-coded, so "without it, S2 would
 * sign off a corpus with no analysis that makes the corpus mean anything."
 *
 * WHAT COUNTS AS A FALSE ALLOW HERE. Ground truth is the INDEPENDENT LABEL, never the
 * engine's own output. A false allow is a fixture the labellers said BLOCK or REVIEW and a
 * layer allowed; a false block is one they said ALLOW and a layer blocked. Scoring against
 * the engine's own verdict would make L3 perfect by construction, which is the exact
 * circularity D-006 and D-011 exist to break.
 *
 * REVIEW IS NOT A FREE PASS. A layer that reviews where the truth is BLOCK has not detected
 * the attack — it has declined to decide, and §3.3(7) says a review is executable with an
 * owner override while a block is not. So review-where-block-is-true is counted separately
 * and never folded into "detected". Folding it in is the single easiest way to make an
 * ablation table flatter than the system.
 *
 * §7.3's closing instruction is load-bearing and is reproduced in the output: "Do not claim
 * general transaction-safety accuracy."
 */

const REPO = join(import.meta.dirname, "..", "..", "..");
const CORPUS_DIR = join(REPO, "fixtures", "corpus");

type Label = "ALLOW" | "BLOCK" | "REVIEW" | "INSUFFICIENT";

interface LabelRecord {
    fixtureId: string;
    label: Label;
    primaryReason: string;
    specBasis: string;
    confidence: string;
    notes?: string;
}

interface ResultRecord {
    fixtureId: string;
    class: string;
    intent: string;
    primaryEnforcement: string;
    simulated: boolean;
    layers: {layer: LayerName; verdict: string; failing: string[]; micros: number}[];
}

function readJson<T>(path: string): T {
    return JSON.parse(readFileSync(path, "utf8")) as T;
}

function percentile(sorted: number[], p: number): number {
    if (sorted.length === 0) return 0;
    const idx = Math.min(sorted.length - 1, Math.floor((p / 100) * sorted.length));
    return sorted[idx]!;
}

export interface AblationInputs {
    results: ResultRecord[];
    labelsA: LabelRecord[];
    labelsB: LabelRecord[];
}

export function loadInputs(): AblationInputs {
    const index = readJson<{id: string}[]>(join(CORPUS_DIR, "results", "_index.json"));
    const results = index.map((e) => readJson<ResultRecord>(join(CORPUS_DIR, "results", `${e.id}.json`)));

    const aPath = join(CORPUS_DIR, "labels", "labeller-A.json");
    const bPath = join(CORPUS_DIR, "labels", "labeller-B.json");
    if (!existsSync(aPath)) throw new Error(`missing ${aPath}: the independent labelling has not run`);

    return {
        results,
        labelsA: readJson<LabelRecord[]>(aPath),
        labelsB: existsSync(bPath) ? readJson<LabelRecord[]>(bPath) : [],
    };
}

export interface LayerScore {
    layer: LayerName;
    allow: number;
    block: number;
    review: number;
    /** Truth is BLOCK or REVIEW, the layer allowed. The dangerous error. */
    falseAllow: string[];
    /** Truth is ALLOW, the layer blocked. The costly-but-safe error. */
    falseBlock: string[];
    /** Truth is BLOCK, the layer reviewed. Not a detection — an abstention. */
    reviewedWhereBlockIsTrue: string[];
    /** Truth is REVIEW, the layer blocked. Over-strict rather than unsafe. */
    blockedWhereReviewIsTrue: string[];
    exactMatch: number;
    scored: number;
    p50Micros: number;
    p95Micros: number;
}

export function scoreLayer(
    layer: LayerName,
    results: ResultRecord[],
    truth: Map<string, Label>,
): LayerScore {
    const score: LayerScore = {
        layer,
        allow: 0,
        block: 0,
        review: 0,
        falseAllow: [],
        falseBlock: [],
        reviewedWhereBlockIsTrue: [],
        blockedWhereReviewIsTrue: [],
        exactMatch: 0,
        scored: 0,
        p50Micros: 0,
        p95Micros: 0,
    };

    const times: number[] = [];

    for (const r of results) {
        const lr = r.layers.find((l) => l.layer === layer);
        if (lr === undefined) continue;
        times.push(lr.micros);

        if (lr.verdict === "ALLOW") score.allow++;
        else if (lr.verdict === "BLOCK") score.block++;
        else score.review++;

        const t = truth.get(r.fixtureId);
        // A fixture the labellers could not decide is EXCLUDED from accuracy rather than
        // scored as agreement. Counting an INSUFFICIENT as a match would inflate every layer
        // equally and quietly, which is worse than a smaller denominator.
        if (t === undefined || t === "INSUFFICIENT") continue;
        score.scored++;

        if (lr.verdict === t) score.exactMatch++;
        if (lr.verdict === "ALLOW" && t !== "ALLOW") score.falseAllow.push(r.fixtureId);
        if (lr.verdict === "BLOCK" && t === "ALLOW") score.falseBlock.push(r.fixtureId);
        if (lr.verdict === "REVIEW" && t === "BLOCK") score.reviewedWhereBlockIsTrue.push(r.fixtureId);
        if (lr.verdict === "BLOCK" && t === "REVIEW") score.blockedWhereReviewIsTrue.push(r.fixtureId);
    }

    times.sort((a, b) => a - b);
    score.p50Micros = percentile(times, 50);
    score.p95Micros = percentile(times, 95);
    return score;
}

/** D-011(c): the inter-labeller disagreement rate, and the fixtures behind it. */
export function disagreement(a: LabelRecord[], b: LabelRecord[]) {
    const byId = new Map(a.map((r) => [r.fixtureId, r]));
    const compared: {fixtureId: string; a: Label; b: Label; agree: boolean}[] = [];
    for (const rb of b) {
        const ra = byId.get(rb.fixtureId);
        if (ra === undefined) continue;
        compared.push({fixtureId: rb.fixtureId, a: ra.label, b: rb.label, agree: ra.label === rb.label});
    }
    const disagreed = compared.filter((c) => !c.agree);
    return {
        sampleSize: compared.length,
        disagreed,
        ratePercent: compared.length === 0 ? 0 : (100 * disagreed.length) / compared.length,
        compared,
    };
}

/** Detection contribution by layer: what each layer caught that the one before it did not. */
export function contributionByLayer(results: ResultRecord[], truth: Map<string, Label>) {
    const caught = (layer: LayerName) =>
        new Set(
            results
                .filter((r) => {
                    const t = truth.get(r.fixtureId);
                    if (t === undefined || t === "INSUFFICIENT" || t === "ALLOW") return false;
                    const v = r.layers.find((l) => l.layer === layer)?.verdict;
                    // Only a BLOCK counts as catching a BLOCK. A review is an abstention.
                    return t === "BLOCK" ? v === "BLOCK" : v === "REVIEW" || v === "BLOCK";
                })
                .map((r) => r.fixtureId),
        );

    const l1 = caught("L1_baseline");
    const l2 = caught("L2_policy_plus_effects");
    const l3 = caught("L3_full_conformance");

    return {
        l1: [...l1].sort(),
        addedByL2: [...l2].filter((id) => !l1.has(id)).sort(),
        addedByL3: [...l3].filter((id) => !l2.has(id)).sort(),
        lostByL2: [...l1].filter((id) => !l2.has(id)).sort(),
        lostByL3: [...l2].filter((id) => !l3.has(id)).sort(),
    };
}

export function byAttackClass(results: ResultRecord[], truth: Map<string, Label>) {
    const classes = [...new Set(results.map((r) => r.class))].sort();
    return classes.map((cls) => {
        const inClass = results.filter((r) => r.class === cls);
        const row: Record<string, unknown> = {class: cls, fixtures: inClass.length};
        for (const layer of LAYERS) {
            const s = scoreLayer(layer, inClass, truth);
            row[layer] = {
                falseAllow: s.falseAllow.length,
                falseBlock: s.falseBlock.length,
                exactMatch: `${s.exactMatch}/${s.scored}`,
            };
        }
        return row;
    });
}

export function buildReport(inputs: AblationInputs): string {
    const {results, labelsA, labelsB} = inputs;
    const truth = new Map<string, Label>(labelsA.map((l) => [l.fixtureId, l.label]));
    const scores = LAYERS.map((l) => scoreLayer(l, results, truth));
    const dis = disagreement(labelsA, labelsB);
    const contrib = contributionByLayer(results, truth);

    const lines: string[] = [];
    const w = (s = "") => lines.push(s);

    w("# §7.3 Security Ablation Report");
    w();
    w("Generated by `npm --prefix ts run ablation`. Ground truth is the independent labelling");
    w("of D-011, never the engine's own output — scoring against the engine would make the full");
    w("configuration perfect by construction, which is the circularity D-006 exists to break.");
    w();
    w("**§7.3, verbatim: do not claim general transaction-safety accuracy.** These numbers");
    w("describe 50 fixtures over two demo contracts and two call schemas. They are not an");
    w("accuracy claim about EVM transactions, and nothing here is a comparison with any named");
    w("vendor — D-001 cut executed vendor comparisons from v1 entirely.");
    w();

    w("## Configurations");
    w();
    for (const layer of LAYERS) {
        w(`**${layer}** — ${LAYER_DESCRIPTIONS[layer]}`);
        w();
    }

    w("## Results by layer");
    w();
    w("| Layer | allow | block | review | false allow | false block | exact match | p50 µs | p95 µs |");
    w("|---|---:|---:|---:|---:|---:|---:|---:|---:|");
    for (const s of scores) {
        w(
            `| ${s.layer} | ${s.allow} | ${s.block} | ${s.review} | **${s.falseAllow.length}** | ` +
                `${s.falseBlock.length} | ${s.exactMatch}/${s.scored} | ${s.p50Micros.toFixed(0)} | ` +
                `${s.p95Micros.toFixed(0)} |`,
        );
    }
    w();
    w("`false allow` is the dangerous error: the independent labels said block or review and the");
    w("layer allowed. `false block` is the costly-but-safe one. They are reported separately");
    w("because averaging them into one accuracy number hides which kind a configuration makes.");
    w();

    w("### Abstentions, counted separately from detections");
    w();
    for (const s of scores) {
        w(
            `- **${s.layer}** — reviewed where the truth is BLOCK: ${s.reviewedWhereBlockIsTrue.length}` +
                (s.reviewedWhereBlockIsTrue.length ? ` (${s.reviewedWhereBlockIsTrue.join(", ")})` : "") +
                `; blocked where the truth is REVIEW: ${s.blockedWhereReviewIsTrue.length}` +
                (s.blockedWhereReviewIsTrue.length ? ` (${s.blockedWhereReviewIsTrue.join(", ")})` : ""),
        );
    }
    w();
    w("A review where the truth is a block is **not a detection**. §3.3(7) makes a review");
    w("executable with an owner override while a block is not, so treating the two as equivalent");
    w("would credit a configuration for holding a door it left openable.");
    w();

    w("## Detection contribution by layer");
    w();
    w(`- Caught by the baseline alone: ${contrib.l1.length} — ${contrib.l1.join(", ") || "none"}`);
    w(`- **Added by effect extraction (L2): ${contrib.addedByL2.length}** — ${contrib.addedByL2.join(", ") || "none"}`);
    w(`- **Added by mandate conformance (L3): ${contrib.addedByL3.length}** — ${contrib.addedByL3.join(", ") || "none"}`);
    if (contrib.lostByL2.length) w(`- Regressed at L2 (caught by L1, missed by L2): ${contrib.lostByL2.join(", ")}`);
    if (contrib.lostByL3.length) w(`- Regressed at L3 (caught by L2, missed by L3): ${contrib.lostByL3.join(", ")}`);
    w();

    w("## Inter-labeller disagreement (D-011c)");
    w();
    w(`Sample: ${dis.sampleSize} fixtures re-labelled by a second independent labeller.`);
    w(`**Disagreement rate: ${dis.ratePercent.toFixed(1)}%** (${dis.disagreed.length}/${dis.sampleSize}).`);
    w();
    w("D-011(d) declares the thresholds in advance: **>10% halts S2 pending corpus review**, and");
    w("**any disagreement on a hard-gate-relevant fixture escalates to John individually**");
    w("regardless of the aggregate rate.");
    w();
    if (dis.disagreed.length > 0) {
        w("| Fixture | Labeller A | Labeller B |");
        w("|---|---|---|");
        for (const d of dis.disagreed) w(`| ${d.fixtureId} | ${d.a} | ${d.b} |`);
        w();
    }
    w(
        dis.ratePercent > 10
            ? "**THRESHOLD BREACHED — S2 halts pending corpus review (D-011d).**"
            : "Rate is within the declared threshold.",
    );
    w();

    w("## Results by attack class");
    w();
    w("| Class | n | L1 false allow | L2 false allow | L3 false allow |");
    w("|---|---:|---:|---:|---:|");
    for (const row of byAttackClass(results, truth)) {
        const cell = (l: LayerName) => (row[l] as {falseAllow: number}).falseAllow;
        w(
            `| ${row.class} | ${row.fixtures} | ${cell("L1_baseline")} | ` +
                `${cell("L2_policy_plus_effects")} | ${cell("L3_full_conformance")} |`,
        );
    }
    w();

    w("## Dependency-failure behaviour (§7.3)");
    w();
    const depFixtures = results.filter((r) => !r.simulated);
    w(`${depFixtures.length} fixtures ran with no simulation available — the §3.3(8) critical-`);
    w("dependency path. Their verdicts by layer:");
    w();
    for (const r of depFixtures) {
        const v = r.layers.map((l) => `${l.layer}=${l.verdict}`).join(", ");
        w(`- \`${r.fixtureId}\` — ${v}`);
    }
    w();
    w("§3.3(8) requires that a critical dependency failure never produce an automatic allow.");
    w("Whether each of these satisfies that is the labels' call, and is scored above.");
    w();

    w("## Attribution note");
    w();
    w("Some fixtures' primary enforcement is not the conformance engine, and counting them");
    w("against it would misattribute the evidence:");
    w();
    for (const r of results.filter((r) => r.primaryEnforcement !== "conformance-engine")) {
        w(`- \`${r.fixtureId}\` — ${r.primaryEnforcement}`);
    }
    w();

    return lines.join("\n") + "\n";
}

if (import.meta.filename === process.argv[1]) {
    const inputs = loadInputs();
    const report = buildReport(inputs);
    const out = join(REPO, "docs", "ablation-report.md");
    writeFileSync(out, report);
    console.log(report);
    console.log(`\nwrote ${out}`);
}
