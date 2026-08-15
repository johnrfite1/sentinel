import {describe, it} from "node:test";
import assert from "node:assert/strict";
import {keccak256, stringToBytes} from "viem";
import {
    BASELINE_CODES,
    baselineVerdict,
    runBaseline,
    type BaselineConfig,
} from "../src/ablation/baseline.ts";
import {LAYERS, MANDATE_CONFORMANCE_CODES, runLayer} from "../src/ablation/layers.ts";
import {EVAL_CODES, EVAL_EXECUTABILITY_CODES, runChecks, verdictOf, type ConformanceInput} from "../src/evaluate/checks.ts";
import {decodeCall, buildRegistry, MAX_UINT256} from "../src/decode/index.ts";
import {hashMandate, hashPolicy} from "../src/evaluate/hashes.ts";
import type {Hex, MandatePayload, PolicyPayload, ActionPayload} from "../src/signer/protocol.ts";
import type {VaultState} from "../src/signer/vault.ts";

/**
 * The §7.2 baseline and the §7.3 layer partition.
 *
 * WHY THIS FILE EXISTS. The ablation's headline claim is a comparison, and a comparison is
 * only as honest as its weaker arm. If the baseline is accidentally weak — or if the layer
 * partition accidentally leaves a mandate check inside L2 — the resulting table overstates
 * or understates Sentinel's contribution, and it does so while looking entirely plausible.
 * Neither failure would turn a test red without these.
 *
 * COVERAGE BOUNDARY. These prove the baseline enforces what §7.2 grants it and withholds
 * what §7.2 withholds, and that the layer partition names real checks. They say nothing
 * about whether any verdict is correct — that is the independently labelled corpus.
 */

const DEMOPAY: Hex = "0x5fbdb2315678afecb367f032d93f642f64180aa3";
const DEMO_ERC20: Hex = "0xe7f1725e7734ce288f8367e1bb143e90bb3f0512";
const OWNER: Hex = "0xf39fd6e51aad88f6f4ce6ab8827279cfffb92266";
const ATTACKER: Hex = "0x00000000000000000000000000000000deadbeef";
const VAULT: Hex = "0x0000000000000000000000000000000000000abc";
const RESOURCE: Hex = keccak256(stringToBytes("weather-basic-24h"));
const WRONG_RESOURCE: Hex = keccak256(stringToBytes("premium-monthly"));
const CHAIN = 31_337n;
const CEILING = 10n ** 16n;

const registry = buildRegistry({[DEMOPAY]: "DemoPay", [DEMO_ERC20]: "DemoERC20"});

const config: BaselineConfig = {
    chainId: CHAIN,
    vault: VAULT,
    allowedTargets: [DEMOPAY, DEMO_ERC20],
    allowedSelectors: ["0xc188528b", "0x095ea7b3"],
    maxNativeValueWei: CEILING,
    blockUnlimitedApproval: true,
};

function purchaseCalldata(resource: Hex, beneficiary: Hex = OWNER, duration = 86_400n, recurring = false): Hex {
    return ("0xc188528b" +
        resource.slice(2) +
        beneficiary.slice(2).padStart(64, "0") +
        duration.toString(16).padStart(64, "0") +
        (recurring ? "1" : "0").padStart(64, "0")) as Hex;
}

function approveCalldata(spender: Hex, amount: bigint): Hex {
    return ("0x095ea7b3" +
        spender.slice(2).padStart(64, "0") +
        amount.toString(16).padStart(64, "0")) as Hex;
}

const policy: PolicyPayload = {
    schemaVersion: 1n,
    policyVersion: 1n,
    vault: VAULT,
    chainId: CHAIN,
    allowedOperation: 0n,
    allowedTargetsHash: keccak256(stringToBytes("targets")),
    allowedSelectorsHash: keccak256(stringToBytes("selectors")),
    maxNativeValueWei: CEILING,
    maxAllowanceIncreaseBaseUnits: 0n,
    allowedCallGraphHash: keccak256(stringToBytes("graph")),
    validAfter: 0n,
    validUntil: 4_000_000_000n,
    failureMode: 1n,
};

const mandate: MandatePayload = {
    schemaVersion: 1n,
    mandateId: keccak256(stringToBytes("m")),
    principal: OWNER,
    vault: VAULT,
    chainId: CHAIN,
    target: DEMOPAY,
    targetCodeHash: keccak256(stringToBytes("code")),
    selector: "0xc188528b",
    maxNativeValueWei: CEILING,
    purposeKind: keccak256(stringToBytes("purpose")),
    resourceId: RESOURCE,
    beneficiary: OWNER,
    durationSeconds: 86_400n,
    recurringAllowed: false,
    validAfter: 0n,
    validUntil: 4_000_000_000n,
    policyHash: hashPolicy(policy),
};

const vaultState: VaultState = {
    owner: OWNER,
    signer: OWNER,
    activeMandateHash: hashMandate(mandate),
    activePolicyHash: hashPolicy(policy),
    actionNonce: 0n,
    paused: false,
    maxNativeValueWei: CEILING,
    targetAllowed: true,
    selectorAllowed: true,
    domainSeparator: keccak256(stringToBytes("d")),
    targetCodeHash: keccak256(stringToBytes("code")),
    observedAtBlock: 1n,
};

function input(overrides: {
    target?: Hex;
    callData?: Hex;
    valueWei?: bigint;
    action?: Partial<ActionPayload>;
}): ConformanceInput {
    const target = overrides.target ?? DEMOPAY;
    const callData = overrides.callData ?? purchaseCalldata(RESOURCE);
    const action: ActionPayload = {
        schemaVersion: 1n,
        chainId: CHAIN,
        vault: VAULT,
        actionNonce: 0n,
        target,
        valueWei: overrides.valueWei ?? 10n ** 15n,
        dataHash: keccak256(callData),
        operation: 0n,
        mandateHash: vaultState.activeMandateHash,
        policyHash: vaultState.activePolicyHash,
        deadline: 4_000_000_000n,
        ...overrides.action,
    };
    return {
        mandate,
        policy,
        action,
        callData,
        decode: decodeCall({target, callData, registry}),
        simulation: null,
        vaultState,
        now: 1_000_000n,
    };
}

function codesOf(results: {code: string; outcome: string}[], outcome: string): string[] {
    return results.filter((r) => r.outcome === outcome).map((r) => r.code);
}

// ---------------------------------------------------------------------------

describe("the §7.2 baseline enforces what §7.2 grants it", () => {
    const triggers: {code: string; why: string; input: ConformanceInput}[] = [
        {
            code: "BASE_CHAIN_BOUND",
            why: "a different chain id",
            input: input({action: {chainId: 8_453n}}),
        },
        {
            code: "BASE_VAULT_BOUND",
            why: "a different vault",
            input: input({action: {vault: "0x000000000000000000000000000000000000dead"}}),
        },
        {
            code: "BASE_TARGET_ALLOWLISTED",
            why: "a target that is not on the allowlist",
            input: input({target: "0x000000000000000000000000000000000000beef"}),
        },
        {
            code: "BASE_SELECTOR_ALLOWLISTED",
            why: "a selector that is not on the allowlist",
            input: input({callData: ("0xdeadbeef" + "0".repeat(64)) as Hex}),
        },
        {
            code: "BASE_VALUE_CEILING",
            why: "native value above the ceiling",
            input: input({valueWei: CEILING + 1n}),
        },
        {
            code: "BASE_UNLIMITED_APPROVAL",
            why: "an unlimited approval",
            input: input({target: DEMO_ERC20, callData: approveCalldata(ATTACKER, MAX_UINT256), valueWei: 0n}),
        },
    ];

    for (const t of triggers) {
        it(`${t.code} — ${t.why}`, () => {
            const results = runBaseline(t.input, config);
            assert.ok(
                codesOf(results, "VIOLATION").includes(t.code),
                `expected ${t.code}, got ${JSON.stringify(results)}`,
            );
            assert.equal(baselineVerdict(results), "BLOCK");
        });
    }

    it("BASE_CALLDATA_UNDECODABLE — calldata it cannot read", () => {
        // An ALLOWLISTED selector carrying the wrong number of argument words. Two-byte
        // calldata would not isolate this: the baseline blocks it on BASE_SELECTOR_ALLOWLISTED
        // first, which is correct behaviour and would have made the verdict assertion below
        // pass for the wrong reason.
        const short = ("0xc188528b" + RESOURCE.slice(2) + "0".repeat(64)) as Hex;
        const results = runBaseline(input({callData: short}), config);
        assert.ok(codesOf(results, "UNRESOLVED").includes("BASE_CALLDATA_UNDECODABLE"));
        // The verdict, not just the code. Mutation B5 changed the baseline's fold so an
        // UNRESOLVED check blocks, and the suite stayed green: the code was asserted and the
        // consequence was not. That consequence is the whole point — a wallet policy that
        // cannot decode a call applies the rules it could evaluate rather than holding the
        // transaction, which is what makes this a FALSE ALLOW in the ablation and what stops
        // the baseline being quietly credited with a detection it never made.
        assert.equal(baselineVerdict(results), "ALLOW");
    });

    it("allows the conforming action", () => {
        const results = runBaseline(input({}), config);
        assert.deepEqual(codesOf(results, "VIOLATION"), []);
        assert.equal(baselineVerdict(results), "ALLOW");
    });

    /**
     * Structural, in the style the rest of this repo uses: enumerate the module's own
     * declared surface so a code added later without a trigger turns this file red.
     */
    it("has a trigger for every declared baseline code", () => {
        const covered = new Set([...triggers.map((t) => t.code), "BASE_CALLDATA_UNDECODABLE"]);
        const missing = BASELINE_CODES.filter((c) => !covered.has(c));
        assert.deepEqual(missing, [], "every BASELINE_CODES entry needs its own trigger");
    });
});

describe("the §7.2 baseline withholds what §7.2 withholds", () => {
    /**
     * §7.2, verbatim: "No resource, beneficiary, duration, recurrence, or post-state
     * constraint." This is the property that makes the whole ablation meaningful — if the
     * baseline caught a wrong-purpose action, §4.2 Case 3 would demonstrate nothing.
     *
     * Asserted as a LIMIT rather than a capability, which is the pattern this repo already
     * uses for `signer.e2e.test.ts`: when the claim changes, the test fails and points at it.
     */
    const wrongPurpose: [string, Hex][] = [
        ["a resource the mandate does not name", purchaseCalldata(WRONG_RESOURCE)],
        ["the attacker as beneficiary", purchaseCalldata(RESOURCE, ATTACKER)],
        ["thirty days where the mandate says one", purchaseCalldata(RESOURCE, OWNER, 30n * 86_400n)],
        ["recurrence enabled against a mandate that forbids it", purchaseCalldata(RESOURCE, OWNER, 86_400n, true)],
    ];

    for (const [why, callData] of wrongPurpose) {
        it(`allows ${why}`, () => {
            const results = runBaseline(input({callData}), config);
            assert.equal(
                baselineVerdict(results),
                "ALLOW",
                "a baseline that caught this would make §4.2 Case 3 vacuous",
            );
        });
    }

    it("allows a finite approval the mandate never authorised", () => {
        const results = runBaseline(
            input({target: DEMO_ERC20, callData: approveCalldata(ATTACKER, 10n ** 9n), valueWei: 0n}),
            config,
        );
        assert.equal(baselineVerdict(results), "ALLOW");
    });

    it("never renders REVIEW — it is a two-verdict engine", () => {
        for (const t of [input({}), input({valueWei: CEILING + 1n}), input({callData: "0xc188" as Hex})]) {
            assert.notEqual(baselineVerdict(runBaseline(t, config)), "REVIEW");
        }
    });
});

// ---------------------------------------------------------------------------

describe("the §7.3 layer partition", () => {
    /**
     * THE MOST IMPORTANT TEST IN THIS FILE.
     *
     * `MANDATE_CONFORMANCE_CODES` is a hand-written list of strings, and L2 is defined as the
     * engine MINUS that list. A single typo — a renamed code, a stale entry — would silently
     * leave a mandate check inside L2, and the ablation would report that effect extraction
     * catches wrong-purpose actions. The table would look plausible and be wrong.
     *
     * Nothing else in the system would notice, because a `Set` of strings never fails to
     * match a name that does not exist.
     */
    it("names only codes the engine actually declares", () => {
        const declared = new Set<string>(EVAL_CODES);
        const unknown = [...MANDATE_CONFORMANCE_CODES].filter((c) => !declared.has(c));
        assert.deepEqual(
            unknown,
            [],
            "a code here that the engine does not declare silently leaves a check inside L2",
        );
    });

    /**
     * Same structural guard as MANDATE_CONFORMANCE_CODES, and for the same reason: a hand-
     * written Set of strings never fails to match a name that does not exist. An entry here
     * that the engine does not declare would make §3.3(7)'s amended remedy clause point at a
     * code nobody can ever see, and nothing else would notice.
     */
    it("EVAL_EXECUTABILITY_CODES names only codes the engine declares (D-026)", () => {
        const declared = new Set<string>(EVAL_CODES);
        const unknown = [...EVAL_EXECUTABILITY_CODES].filter((c) => !declared.has(c));
        assert.deepEqual(unknown, [], "an executability code the engine does not declare");
        assert.ok(EVAL_EXECUTABILITY_CODES.size > 0);
    });

    it("keeps executability and mandate-conformance disjoint (D-026)", () => {
        // A code in both classes would make the remedy ambiguous — the whole point of the
        // classification is that one needs a new mandate and the other does not.
        const overlap = [...EVAL_EXECUTABILITY_CODES].filter((c) => MANDATE_CONFORMANCE_CODES.has(c));
        assert.deepEqual(overlap, [], "a code cannot be both executability and mandate conformance");
    });

    it("removes something — L2 is not just L3 under another name", () => {
        assert.ok(MANDATE_CONFORMANCE_CODES.size > 0);
        const full = runChecks(input({}));
        const l2 = full.filter((c) => !MANDATE_CONFORMANCE_CODES.has(c.code));
        assert.ok(l2.length < full.length, "L2 must be strictly smaller than L3");
    });

    it("L3 is the full engine, unmodified", () => {
        const i = input({});
        const l3 = runLayer("L3_full_conformance", i, config);
        const direct = runChecks(i);
        assert.deepEqual(
            l3.checks.map((c) => c.code).sort(),
            direct.map((c) => c.code).sort(),
        );
        assert.equal(l3.verdict, verdictOf(direct, i.policy));
    });

    /**
     * THIS ASSERTION CANNOT CURRENTLY OBSERVE THE DEFECT IT IS NAMED FOR, and that is
     * recorded here rather than left for someone to discover.
     *
     * `runLayer` passes L1 an input with `simulation: null` so the baseline structurally
     * cannot see post-state. Mutation B7 removed that and handed the real simulation
     * through; the suite stayed green, because `runBaseline` reads no simulation field at
     * all, so the trap below never fires either way.
     *
     * The `simulation: null` is therefore defence in depth, not currently-load-bearing code:
     * it is what would stop a post-state check added to the baseline later from silently
     * violating §7.2's "no post-state constraint". Kept for that reason, with its
     * untestability stated, per the AGENTS.md rule that a test which cannot detect its own
     * bug must say so in the test file. The trap still guards the day someone does read it.
     */
    it("L1 never consults the simulation (see comment: cannot fail today)", () => {
        const trap = new Proxy(
            {},
            {
                get() {
                    throw new Error("L1 read the simulation; §7.2 grants it no post-state constraint");
                },
            },
        );
        const i = {...input({}), simulation: trap as never};
        assert.doesNotThrow(() => runLayer("L1_baseline", i, config));

        // What IS observable: the baseline's own output must not mention any post-state code.
        const codes = runBaseline(i, config).map((c) => c.code);
        for (const code of codes) {
            assert.equal(code.startsWith("BASE_"), true, `${code} is not a baseline-namespaced code`);
        }
    });

    it("catches the wrong-purpose action at L3 and not at L1 or L2", () => {
        const i = input({callData: purchaseCalldata(WRONG_RESOURCE)});
        const l2 = runLayer("L2_policy_plus_effects", i, config);

        // "Does not block" rather than "allows": this synthetic input carries no simulation,
        // so L2 legitimately REVIEWS on the absent evidence (failureMode = REVIEW). The
        // property under test is that neither L1 nor L2 DETECTS the wrong purpose — which a
        // review is not, per the abstention rule the ablation scores by. The corpus run
        // exercises the same shape with a real simulation (F012: L1 allow, L2 allow, L3 block).
        assert.equal(runLayer("L1_baseline", i, config).verdict, "ALLOW");
        assert.notEqual(l2.verdict, "BLOCK", `L2 failing: ${l2.failing.join(", ")}`);
        assert.equal(
            l2.failing.includes("EVAL_PURCHASE_RESOURCE"),
            false,
            "the wrong-resource check must not survive into L2",
        );
        assert.equal(runLayer("L3_full_conformance", i, config).verdict, "BLOCK");
    });

    /**
     * L1 must fold with the BASELINE's rule, not the engine's.
     *
     * Mutation B7 swapped `baselineVerdict` for `verdictOf` inside `runLayer` and survived:
     * the fold was tested by calling `baselineVerdict` directly, never through the layer. The
     * two disagree exactly where it matters — on an unresolved check, the engine's fold
     * returns REVIEW under `failureMode = REVIEW` while the baseline returns ALLOW — so the
     * mutation would have silently given the baseline a third verdict §7.2 never grants it,
     * and converted a false allow into an abstention in the ablation table.
     */
    it("L1 folds with the baseline's rule, not the engine's", () => {
        const undecodable = ("0xc188528b" + RESOURCE.slice(2) + "0".repeat(64)) as Hex;
        const r = runLayer("L1_baseline", input({callData: undecodable}), config);
        assert.equal(r.verdict, "ALLOW", `L1 must not review; got ${r.verdict}`);
    });

    it("reports a decision latency for every layer", () => {
        for (const layer of LAYERS) {
            const r = runLayer(layer, input({}), config);
            assert.ok(r.micros >= 0 && Number.isFinite(r.micros), `${layer} produced no timing`);
        }
    });
});
