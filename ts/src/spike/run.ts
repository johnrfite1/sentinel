import Anthropic from "@anthropic-ai/sdk";
import {writeFileSync, mkdirSync} from "node:fs";
import {join} from "node:path";
import {scaffoldHash} from "./scaffold.ts";
import {
    REPO_ROOT,
    classify,
    loadEnv,
    runArm,
    verdictOf,
    type ArmResult,
} from "./arms.ts";

/**
 * D-007 injection spike.
 *
 * Runs two arms that differ in exactly one input — the service document the agent
 * retrieves — and records what each one proposed.
 *
 *   control   (benign doc)    → expected: DemoPay.purchase, the Case 1 proposal
 *   treatment (poisoned doc)  → does the proposal flip to DemoERC20.approve?
 *
 * Without the control arm, a flipped treatment proposal is not attributable to the
 * injection; with it, the pair is a demonstration rather than a staged demo.
 *
 * A negative result — the agent resists — is a finding, not a failure. §4's claim is
 * that an *untrusted* agent cannot execute, not that a gullible one is fooled.
 *
 * THE TWO-ARM PROCEDURE ITSELF LIVES IN `arms.ts`, shared with the D-007 canary
 * (`canary.ts`) so both run the same one. A canary running a copy would be answering
 * whether the model matches the copy.
 */

loadEnv();

const MODEL = process.env.SENTINEL_AGENT_MODEL ?? "claude-opus-5";
const client = new Anthropic();

const started = new Date().toISOString();
console.log(`D-007 injection spike\nmodel: ${MODEL}\nscaffold: ${scaffoldHash()}\n`);

const control: ArmResult = await runArm(client, MODEL, "control");
console.log(`control   : reads=${control.docReads} proposals=${control.proposals.length}${control.refused ? ` REFUSED(${control.refusalCategory})` : ""}`);
for (const p of control.proposals) console.log(`            → ${classify(p)}  ${p.function_signature} @ ${p.target}`);

const treatment: ArmResult = await runArm(client, MODEL, "treatment");
console.log(`treatment : reads=${treatment.docReads} proposals=${treatment.proposals.length}${treatment.refused ? ` REFUSED(${treatment.refusalCategory})` : ""}`);
for (const p of treatment.proposals) console.log(`            → ${classify(p)}  ${p.function_signature} @ ${p.target}`);

const controlKinds = control.proposals.map(classify);
const treatmentKinds = treatment.proposals.map(classify);
const verdict = verdictOf(control, treatment);

const record = {
    spike: "D-007",
    startedAt: started,
    finishedAt: new Date().toISOString(),
    model: MODEL,
    servedModel: control.servedModel,
    // Opus 4.7+ removed temperature/top_p/top_k — sending them is a 400. D-007 asks for
    // temperature; on this model there is none to record. Stating that beats recording a
    // value the API never accepted.
    temperature: null,
    temperatureNote: "not settable on this model family (removed on Opus 4.7+)",
    scaffoldHash: scaffoldHash(),
    verdict,
    control: {
        kinds: controlKinds,
        docReads: control.docReads,
        refused: control.refused,
        refusalCategory: control.refusalCategory,
        finalText: control.finalText,
    },
    treatment: {
        kinds: treatmentKinds,
        docReads: treatment.docReads,
        refused: treatment.refused,
        refusalCategory: treatment.refusalCategory,
        finalText: treatment.finalText,
    },
    transcripts: {control: control.transcript, treatment: treatment.transcript},
};

const outDir = join(REPO_ROOT, "fixtures", "injection");
mkdirSync(outDir, {recursive: true});
const outFile = join(outDir, `spike-${MODEL}-${started.replace(/[:.]/g, "-")}.json`);
writeFileSync(outFile, JSON.stringify(record, null, 2));

console.log(`\nVERDICT: ${verdict}`);
console.log(`recorded: ${outFile.replace(REPO_ROOT, ".")}`);
console.log(`\ncontrol final text  : ${control.finalText.slice(0, 300)}`);
console.log(`treatment final text: ${treatment.finalText.slice(0, 300)}`);
