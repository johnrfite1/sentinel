# Sentinel — A-018 remediation register

**This file changes nothing. It records what should change.** It holds the **proposed** remediation
set reflecting build-team evidence and informal chair consultation against the four
Adversary-sustained Cycle 2 Criticals (`A-018` / `MSG-022`, session
`S-20260829-sentinel-enforcement-publication`). **Pending Smith registration and authorization.**

Written 2026-08-30. **Corrected the same day, before any of it was acted on** — see §0.

**THIS REGISTER AUTHORISES NOTHING.** It does not withdraw a Critical, ratify Cycle 2, close a
gate, resolve the publication scope, or authorise a push, a deployment, or a visibility change.
The Crucible line remains **HALTED** with all four Criticals **OPEN AT ANVIL**. Nothing in §3
becomes authorised work by appearing here.

**Nothing here is "agreed" in any ratified sense.** Where an earlier draft said "agreed between
the build team and the Crucible council" or "accepted by the council," it was describing an
**informal consultation with no ledger entry**. The chairs made no ruling and the Smith has made
none. That wording is corrected throughout.

**LINE NUMBERS BELOW ARE SECTION ANCHORS, NOT LINE NUMBERS.** This is the `v1-1-register.md`
rule and it exists because that register's line numbers were stale within hours of being written.
Grep the quoted string; do not trust an integer in a file that moves.

---

## 0. What the first version of this file got wrong

Recorded at the top, in the house pattern, because the largest error was load-bearing and a
reader who skips it will draw the wrong conclusion about urgency.

### 0.1 THE PUSHED-BRANCH CLAIM WAS FALSE

The first version said these were *"live defects and false claims in code that exists on a
pushed branch."* **That is false.** Measured 2026-08-30:

```sh
git rev-parse --short HEAD                              # a38cff9
git rev-parse --short origin/step-3/isolated-signer     # 70f4b4d
git branch -r --contains a38cff9                        # (empty — no remote ref contains it)
```

**`a38cff9` was never pushed.** The BLOCK→PASS verifier and the entire v0.3 publication surface
exist **only in the local working tree.** No recipient has ever been able to obtain them.

**This is prevention work, not incident response,** and the distinction changes the sequencing
argument in §6. The error came from carrying a stale "branch pushed" fact forward — true of
`70f4b4d`, not of `a38cff9` — without re-measuring it. That is exactly the failure the
workspace rule *"verify before you rely on a documented status"* exists to prevent, committed
in a document whose §1 is a list of unverified claims.

### 0.2 Three further corrections

- **Conscience attribution.** The first version said the council's restatement "named only the
  publication policy layer." Wrong as to the Conscience, who named **both**
  `verify_publication.py` and `deployment.py` explicitly (grep `so verifier/verify_publication.py,
  verifier/deployment.py` in the session `comms.md`). Her omission was not separating their
  *consequences*, not failing to name the module.
- **"Valid under every branch."** Overstated. The §3 items are valid **only if the v0.3
  enforcement/verifier architecture is retained.** A fresh casting could remove or redefine them.
  §3 is retitled accordingly.
- **Licence claim.** The first version said `UNLICENSED` leaves recipients "no right to use,
  modify, or independently examine." The examination half is **not established** and is removed
  pending legal review. What holds: `UNLICENSED` provides **no affirmative licence grant**.

---

## 1. Verified facts

Every figure produced by running the tool on 2026-08-30 against `a38cff9`, not by reading prose.

### 1.1 The shipped publication verifier accepts a BLOCK receipt

Reproduced. Signing a deployment manifest with a freshly generated authority key and pointing the
shipped verifier at the `case-2-injection-block` bundle (receipt `verdict` = `0` = BLOCK) returns
`PASS: authenticated deployment, owner mandate, exact action, and current receipt`, exit 0. In the
same run an invented `runtimeCodeHash` was echoed back in the PASS payload, and a receipt expired
nine hours earlier was revived through `--evaluation-time`.

**Not a signature or cryptography failure.** The signatures verify correctly. What the run
demonstrates is the absence of a binding between a signed manifest and live chain state, and the
absence of a verdict check.

### 1.2 Test coverage, and where the boundary falls

| File in `release/verifier/` | Covered by the 221-test suite |
|---|---|
| `eip712.py` | Yes — imported, 73 call sites |
| `jcs.py` | Yes — imported, 39 call sites |
| `keccak.py` | Yes — `keccak256` / `keccak256_hex` imported |
| `secp256k1.py` | Yes — recovery functions imported |
| `verify_publication.py` | **No — never imported by any test** |
| `deployment.py` | **No — never imported by any test** |

The 15 apparent matches for "deployment" in the suite are the English word in comments about the
legacy `domain.json` root, not the module. **The two uncovered files are exactly the two files
`a38cff9` introduced** — verify with
`git log --diff-filter=A -- verifier/deployment.py verifier/verify_publication.py`. The commit
boundary, the coverage boundary and the post-Gate-8 boundary coincide.

`deployment.py` deserves separate emphasis: **it is where the recipient's out-of-band trust
decision enters the system.**

### 1.3 The release tree, stated as a check result and not as an absence

**No known development key was detected by these checks in the enumerated release tree.** The
guard is a denylist — grep `KNOWN_DEV_KEYS` in `scripts/assemble-enforcement-release.py`. An
earlier draft said the tree was "already clean," which asserts an absence a denylist cannot
establish, in a document that criticised `release/README.md` for exactly that.

### 1.4 What the deployment manifest signs

`sourceArchiveHash` covers only `contracts/src/**.sol` (grep `function sourceArchiveHash` in
`ts/src/tools/cold-demo.ts`). The manifest also signs `runtimeCodeHash`, `compilerMetadataHash`,
`deploymentBlockHash`, `chainId`, `vault`, `owner`, and `signer` (grep `FIELDS = frozenset` in
`verifier/deployment.py`). **Selected deployment and compiler facts are signed; the complete
recipient-executed release is not.**

### 1.5 The deployment manifest has no expiry

New finding, 2026-08-30. `deployment.py` validates `issuedAt` as a canonical decimal and **never
compares it to anything** — grep `issuedAt` in that file returns two hits, both structural. A
signed manifest is therefore valid forever, with no revocation path. This is the "manifest lacks
a clear expiration/revocation mechanism" item from the Cycle 2 handoff, now measured.

### 1.6 The candidate mechanically custodies value

Relevant to any zero-VaR product decision (§2). In `contracts/src/SentinelVault.sol`: a `payable`
constructor, `receive() external payable {}`, `function recover(address payable to, ...)`, and
`action.target.call{value: action.valueWei}(callData)`. The cold demo deploys with `10n ** 18n`
wei and `PublicationWithdrawal.t.sol` runs `vm.deal(address(vault), 1 ether)`.

### 1.7 Suite figures

`forge test --root contracts` → **105/105**. `pytest verifier/test_verifier.py` → **221/221**. The
internal record is accurate. The release ships **2 of the 105** Foundry tests and **none** of the
221.

---

## 2. What is NOT required, so it is not rediscovered as work

- **A permanent versioned deployment registry is not binding.** A single immutable,
  independently authenticated deployment record satisfies the written Critical 1 condition.
- **The `AUTHENTIC_BUNDLE` / `EXECUTABLE_AT_BLOCK` / `EXECUTED` names are not binding.** The
  *semantic distinction* between static authenticity and live executability is required; the
  names are not.
- **Aggregate caps, signer epochs, minimum execution intervals and `recurringAllowed`
  enforcement are not automatic closure requirements.** They are What-Must-Be-True entries.
- **Git history rewriting is not entailed** by the fixture-key work. See R-A018-10.

**The derivative obligation that does attach.** A value-at-risk ceiling **cannot be declarative.**
If a non-zero exposure is set, something must enforce it, and the per-action ceiling demonstrably
does not — see the `@dev` header in `SentinelVault.sol` ("AGGREGATE LOSS", "EXECUTION RATE"). The
mechanisms above then return as binding *through the VaR clause*.

**On a zero-VaR product, recorded as an option and not proposed.** A product that never custodies
value would satisfy the clause mechanically. **It is not a labelling exercise, and the current
candidate contradicts it** — §1.6. The chairs' informal view is that it is a coherent product
("authorization router, not value custodian") **only if mechanically true**, which would require
at minimum: rejecting custody; requiring `valueWei == 0` or removing the native-value path; a
narrowly defined supported-action class; and bounding token, approval and administrative
authority — because **zero native value is not zero economic exposure.** A zero-value call can
still transfer tokens, grant approvals, exercise administrative authority, or change ownership
and policy. It would leave every other Critical 4 requirement untouched. **This is a product
decision and is John's.**

---

## 3. Work valid if the v0.3 enforcement/verifier architecture is retained

**Not "valid under every branch"** — a fresh casting could remove or redefine all of it. **None of
it is authorised by this register.** No item may be started without an instruction from John.

**Urgency note, corrected:** these are defects and false claims in the **local, unpushed
candidate**. There is no external exposure and no incident to respond to. See §0.1 and §6.

### R-A018-01 — Enforce the verdict `[CRITICAL 3, clause 4]`

`verify_publication.py` never reads `receipt["verdict"]`. **Closes when** a non-`ALLOW` verdict
fails closed; a `REVIEW` receipt passes only through an explicitly modelled and authenticated
owner override, matching the Vault's `NotAllowVerdict` / `NotReviewVerdict`; and both arms have
negative tests.

### R-A018-02 — Remove the dead nonce check; add an authenticated-block nonce check `[CRITICAL 3, clause 4]`

The current check is `parse_uint("uint256", …) < 0` and **cannot fire.** **Closes when** the dead
branch is deleted and a certifying result checks the Vault's nonce state **at a named,
authenticated block**.

**Responsibility split, corrected:** an offline verifier **cannot consume** the on-chain nonce.
The Vault consumes it atomically at execution; the verifier can only observe it at an
authenticated block. Any offline-only mode must state it cannot establish nonce freshness and
must not print "current receipt."

### R-A018-03 — Bind executability to a trusted time source `[CRITICAL 3, clause 2]`

`--evaluation-time` is registered with `help=argparse.SUPPRESS`. **"Non-overridable clock" is
underspecified** — the operating-system clock is also caller-controlled. **Closes when**
executability uses an **authenticated block timestamp or another explicitly trusted time
source**; injected time survives only in a non-certifying test mode that cannot produce a
certifying result; and a "refused clock override" negative test exists.

### R-A018-04 — Bind deployment identity to live chain state `[CRITICAL 3, clause 3; CRITICAL 1]`

Neither module performs any RPC. A fabricated `runtimeCodeHash` is reported as authenticated
(§1.1). **Closes when** the recorded runtime code hash is compared against live deployed bytecode
or an authenticated state proof at a named block, and results distinguish static authenticity
from executability at a named block.

### R-A018-05 — Implement the missing predicate checks `[CRITICAL 3, clause 5]` — NEW

The first version listed negative *tests* for target, value, selector, operation, policy expiry
and code identity but **no item required implementing those checks** in the shipped predicate.
The verifier currently compares none of them against mandate or policy. **Closes when** the
shipped predicate enforces exact target, value, selector, operation, policy validity, and code
identity where relevant.

### R-A018-06 — Test the two uncovered modules `[CRITICAL 3, clause 5]`

**Closes when** `verify_publication.py` and `deployment.py` have direct adversarial coverage on
the pattern in `verifier/test_verifier.py`. For `deployment.py` specifically, hostile coverage
must include **authority selection, wrong-authority refusal, canonicalization, stale deployment
records (§1.5), rotation and revocation, chain/block/code binding, and deployment
configuration** — not merely malformed JSON.

Minimum negative set for the predicate: unapproved signer, absent mandate proof, future and
expired mandate and receipt, consumed nonce, `BLOCK`, `REVIEW` without override, wrong chain,
wrong Vault, wrong target, wrong value, wrong selector, altered calldata, expired policy,
substituted deployment identity, changed target code, stale state proof, refused clock override.

### R-A018-07 — Authenticate the whole release, and bootstrap that check `[CRITICAL 1]`

The recipient's verifier, the TypeScript runtime and `package-lock.json` sit outside the
authority signature, and `MANIFEST.sha256` is itself unsigned.

**The bootstrap requirement, which the first version missed:** the complete release digest must
be verified **before executing the release's own verifier**, or a substituted verifier attests to
itself. This needs an external standard signature/digest tool or a separately bootstrapped one.

**Closes when** the authority signature binds the full release digest and the candidate commit,
and the digest check runs from outside the release.

### R-A018-08 — Correct every overstated claim `[CRITICAL 2; CRITICAL 3]`

| Location | Claim | Problem |
|---|---|---|
| `release/README.md` | "No private key or fixed private-key fixture is included" | Absence claim a denylist cannot make (§1.3) |
| `release/README.md` | "…policy, and nonce commitments" | The nonce check cannot fire; policy is hash-bound, not enforced |
| `verify_publication.py` | `PASS: … and current receipt` | Survives a caller-chosen clock and a BLOCK verdict |
| `a38cff9` commit subject | "publication-ready Sentinel enforcement" | Stronger than the contract's own `@dev` header |
| `docs/enforcement-release-v0.3.md` | "Signer rotation revokes the active mandate" | True of the *mandate*; reads as a claim about *receipts* that `SentinelVault.sol`'s own correction note contradicts |

**Branch-dependent, and must not be batched with the rest:** the drain-boundary disclosure. Under
a mechanically zero-custody product that disclosure and its demonstration need **different
wording**, so it waits on the product ruling. The other rows are branch-neutral.

### R-A018-09 — Type the cold demo's negative controls `[CRITICAL 1]`

`mustReject` in `ts/src/tools/cold-demo.ts` uses a bare `catch` and scores **any** exception as
`PASS negative`. **Closes when** each negative asserts its expected error selector, exit
classification and failure stage.

### R-A018-10 — Stop the demo presenting its own key as out-of-band `[CRITICAL 2]` — NEW

`cold-demo.ts` generates `authorityKey`, signs the manifest with it, and prints that same address
as `Deployment authority (obtain out of band)`. **Closes when** lab-generated authority is
labelled unmistakably non-production and the demo does not present a self-generated address as an
out-of-band trust root.

### R-A018-11 — Resolve the v0.2 envelope tag on v0.3 material `[CRITICAL 2]` — NEW

`release/ts/src/evaluate/index.ts` emits `schema: "sentinel.evidence.v0.2"` in the v0.3
enforcement release. **D-075 deliberately froze the schema tags**, so this is not an accidental
regression — but a recipient of a v0.3 release reading v0.2-tagged evidence has a comprehension
problem regardless of why the tag is stable. **Closes when** the divergence is either resolved or
disclosed reader-facing. **Changing a schema tag touches signature preimages and is not an
architect's call.**

### R-A018-12 — Make fixture separation structural `[CRITICAL 2]`

The guard is a denylist. The three fixed-key tools are `ts/src/tools/sample-check.ts`,
`ts/src/tools/emit-samples.ts`, `ts/src/corpus/run.ts`.

**Closes when** current tools generate ephemeral keys per run, frozen historical fixtures stay
quarantined and reproducible, and lab and production authority domains are structurally distinct.

**On history:** annotation does **not** remove old keys if full git history is publicly
distributed. The least destructive answer is a **history-free publication export**. **Do not
rewrite history** — that depends on the venue ruling in §4.

### R-A018-13 — Pin the recipient's toolchain — *Acceptance Criterion 5, NOT an A-018 requirement*

Reclassified. Solidity is already exact (`pragma solidity 0.8.28`); Node, Python, Foundry and
Anvil are unpinned. Useful reproducibility work, but **it does not appear in any A-018 withdrawal
condition** and must not be presented as closure work.

---

## 4. Blocked on a ruling that is John's — DO NOT START

- **THE CONSTITUTIONAL QUESTION, AND IT COMES FIRST.** The chairs' informal reading: an
  Override-in-Writing **can** authorize proceeding despite unresolved Criticals, but **does not
  rewrite the Ingot's acceptance or kill conditions.** So a lab product cannot be described as
  satisfying the present finished-enforcement Ingot merely because the Criticals were overridden.
  The clean lab path is **a fresh casting** with new acceptance and kill criteria; the other
  instrument is an Override explicitly recording that publication proceeds **while this Ingot
  remains unsatisfied**, which the chairs consider materially less clean. **Not formally ruled.
  No branch can be costed until it is.**
- **Product identity:** value-custody product versus mechanically non-custodial authorization
  router (§2, §1.6).
- **Named audience, venue, publication surface, and production chain.**
- **Whether the published artifact is the release tree, the public repository, or both** — and
  therefore whether a history-free export is needed. R-A018-12 stops at current tools until ruled.
- **Economic value at risk across native value, tokens, approvals and administrative authority** —
  not native value alone.
- **Owner, signer and deployment-authority custody**, and the independently controlled channel by
  which an authority fingerprint reaches a recipient.
- **Monitoring, incident, security-reporting, support and end-of-support posture.**
- **Licence.** All four contract sources carry `SPDX-License-Identifier: UNLICENSED`, which is not
  the SPDX `Unlicense` identifier, and there is **no `LICENSE` file**. It provides **no
  affirmative licence grant**. Any broader claim awaits legal review (§0.2).
- **The unaided named-audience comprehension test, without source access** — Critical 2's own
  falsifier. It cannot be run by the build team and is listed here so it is not lost.
- **Commissioning the persistent deployment and the independent security review.**
- **The v0.3 corpus relabelling**, still owed under **Acceptance Criterion 7**. Grep `the deep
  provenance comparison correctly refuses` in `docs/session-state.md`.

**A caution the build team owes against itself.** Its response to A-018 estimated the branches at
"roughly a week against several months." **Withdrawn** — no work breakdown, and it compared a
branch whose reachability is unknown against one whose scope is unset.

---

## 5. Requirements that survive outside A-018

Recorded because closing the four withdrawal conditions does not close Cycle 2. Still live:
the named-audience test, a clean publication profile, deep-profile resolution, licensing,
supportability and independent review — **unless the Smith changes the Ingot.**

---

## 6. The open sequencing question, stated without a recommendation the build team may not make

The chairs split three ways on whether to repair before the scope decision:

- **Catalyst and Conscience:** authorize the branch-independent defect repairs now.
- **Adversary:** decide the constitutional question first; the defect batch may be separately
  authorized without deciding the product.
- **Subtractor:** because the defective candidate is local-only and each change creates a new
  SHA, settle scope first and build one replacement candidate.

**The §0.1 correction bears directly on this split.** The build team's own argument for immediate
repair rested on the claim that the defects were on a pushed branch. **They are not.** Whatever
weight that urgency carried should be withdrawn from the Catalyst/Conscience position and
returned to Subtractor's.

**`a38cff9` cannot be repaired and remain the reviewed exact candidate.** Every fix produces a new
SHA requiring fresh exact-commit review, which is an argument for batching whatever is authorized
into **one** replacement candidate rather than trickling it.

---

## 7. Protocol gap, recorded for the Crucible rather than for the builders

The §5 `From` enum has seven values and none is the build team, so a halted line whose closure
conditions are all build work has no defined channel for the builder to answer on. The Conscience
recommends a non-seat `BUILDER` / `RESPONDENT` artifact path in a future protocol revision.
