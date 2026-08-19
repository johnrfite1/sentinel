# V1 — COVERAGE: what I did not reach, stated plainly

Frozen commit `c8d15a76425544148d7da2f8fa0c003feb6ad2b7`. Blind spots below are limits on my
evidence, not findings against the repairs. Where a limit could change a verdict, it says so.

---

## 1. Scope I deliberately did not enter

* **Only `R3-F6` and `R3-F7`.** `R3-F5` (the policy half of the receipt binding) sits in the same
  file and I read its tests while enumerating, but I ran no mutation against it and take no
  position on it. Its two tests appear in my output only as bystanders.
* **Nothing in `ts/`, `verifier/`, `scripts/`, `fixtures/` or `corpus/`.** `R3-F6`'s parent
  defect `D-06` was a TypeScript repair never carried to Solidity. I verified the Solidity half
  only. **I cannot say whether the engine's ten comparison edges are still pinned**, and nothing
  here should be read as re-confirming them.
* **No gate run.** Everything is `forge test` on the **default, unseeded** profile. The `gate`
  profile (`fuzz.runs = 20000`, `invariant.runs = 2048`, `seed = 0x53656e74696e656c`) was not
  run. `contracts/foundry.toml`'s own comment records that a mutation killed only by a rare
  sequence could flip between runs. **Consequence: my `SURVIVED` results are single unseeded
  samples.** The decisive one — `F7-ActionExecuted-SUBVIAOVERRIDE-v2` — does not depend on this,
  because I show the defect is killed by a deterministic unit assertion I wrote; a fuzz campaign
  is not what was missing. The two `F6-RESID-OVR-OWN-*` survivals are weaker on this point and
  are recorded as residuals rather than findings partly for that reason.
* **No deployed or forked-chain testing.** All observations are in-process Foundry.

## 2. Enumeration limits

* **The required event set in `REPORT.md` 2.2 is my reading of the specification.** The mapping
  from section 3.3(2)'s six operations onto eight events is an interpretive step, not a
  measurement. The mechanical part — eight events declared, eight emit sites, six state-changing
  `onlyOwner` functions all emitting, every event carrying at least one `expectEmit` — is
  measured. **If the required set is defined differently, the `R3-F7` verdict can move**, which
  is exactly why the scoping question is put to John in `REPORT.md` 2.6 rather than resolved.
* **I did not enumerate events across inheritance.** `SentinelVault` inherits from nothing and
  the only library it uses is OpenZeppelin `ECDSA`, so `grep "^\s*event "` over
  `contracts/src/` is complete for this contract. It would not be for a contract with a base.
* **`DemoPay.Purchased` is excluded by judgement**, as a demo-target event outside the vault's
  audit record. If the guarantee is read to cover the whole demo path, that is one more event I
  did not test.
* **`src/demo/DemoERC20.sol` was not inspected at all.** It appears in neither enumeration.

## 3. Mutation coverage limits

* **Field substitutions are sampled, not exhaustive.** For multi-field events I mutated one or
  two fields, not all. Specifically **not** mutated: `OverrideAuthorized.reviewReceiptHash` and
  `.overrideHash`; `ActionExecuted.actionHash`. My argument that they are covered rests on the
  `expectEmit` flag combinations (topics 1 and 2 checked, `checkData = true` covering every
  non-indexed field) plus the field substitutions that were measured — an inference, not a
  measurement, for those three fields.
* **SUBEVENT (event-swap) was run for two events only** — `MandateActivated` and
  `MandateRevoked`, chosen because they share an ABI shape so the swap compiles. Both were
  caught, which establishes empirically that `vm.expectEmit` checks topic 0 and therefore that
  every other assertion would catch a swap too. **That generalisation is an inference from two
  measurements**, and I am naming it as one because this project's recorded failure mode is
  exactly a generalisation nobody checked.
* **No mutation of the test files themselves.** I did not check whether a test could be silently
  weakened — for example an `expectEmit` flag flipped from `true` to `false` — and still pass
  whatever guard `scripts/test.sh` applies. A guard that ratchets suite counts would not notice.
* **`scripts/mutate.sh` was not run.** I built my own driver rather than reuse the repository's,
  precisely so this would be an independent instrument; the cost is that my results and the
  repository's harness have not been reconciled, and the S-numbered mutants (`S5`, `S6`, ...)
  referenced in the test NatSpec are not the mutants I ran.

## 4. Things I checked shallowly

* **`vm.expectEmit` topic-0 semantics** — established empirically by two caught swaps rather
  than from Foundry documentation. See above.
* **The `deny = "warnings"` interaction** was discovered by three failed builds, not anticipated.
  Any mutation class that orphans a symbol is harder to express here than it looks, and a less
  careful sweep would have scored those three as survivors. I cannot rule out that other
  mutations I considered and rejected as "would not compile" were rejected too quickly.
* **The `_domainSeparator` / signature machinery** is assumed correct throughout. Every probe I
  wrote signs with the same helpers the shipped tests use. If those helpers are wrong, my probes
  are wrong in the same direction — though the boundary mutations would still discriminate,
  since they turn on time and not on signatures.

## 5. What a reader should not conclude from this review

* **Not** that the vault's timestamp policy is correct — only that all three of its boundaries
  are pinned in both directions. The tests assert an instrument, as the file itself says.
* **Not** that the event set is complete against the specification — only that eight events
  exist, that seven of them are fully instrumented, and that the eighth is instrumented on one
  of its two paths.
* **Not** that `R3-F7`'s repair is poor work. Its own six events are the strongest-pinned
  surfaces I touched. The `FAIL` is about the boundary of the claim, not the quality inside it.
* **Not** anything about the other three items in this cycle, or about the checkpoint as a whole.

## 6. Open question recorded for John, not answered

Does `R3-F7` close on the six events its repair scoped — with the
`ActionExecuted.viaOverride` gap raised as a separate item against D-043's coverage — or does it
stay open until every event in the required set detects both omission and substitution on every
path that can emit it? I have taken the second reading because that is what `BRIEF-V1.md` asks
for, and I have no authority to narrow it. The decision is John's.
