# D-010 Receipt-Verifier CLI — Independent Reimplementation Report

Authored by the independent verifier subagent (2026-08-15), which read only
`Sentinel_Protocol_Lab_Proposal_v0_2.md` and `fixtures/samples/**`. It never opened `ts/`,
`contracts/`, `scripts/`, or `docs/`. Transcribed into the repository by the build loop
because the subagent's tooling could not write it; the content is the subagent's.

## 0. Headline

**§5 as written is not sufficient to build a verifier.** Not "ambiguous in places" —
insufficient. Of the six hash computations a Sentinel receipt depends on, §5 supplies enough
to reproduce exactly **one** (`evidenceHash`, because §5.6 names RFC 8785 and keccak256). The
other five — `mandateHash`, `policyHash`, `actionHash`, `reasonCodesHash`, and the EIP-712
digest itself — are named as fields and never defined.

Four of the five were recovered by brute-force search against the signed samples. The fifth,
`reasonCodesHash`, could not be recovered at all; the CLI reports it as `NOT VERIFIABLE`
rather than pretending otherwise.

> **Amended 2026-08-15 (D-022).** The preceding paragraph is preserved as written but is no
> longer current. §5.4 now defines `reasonCodesHash`, the samples publish the `reasonCodes`
> array the construction needs, and the CLI recomputes and checks it — the `NOT VERIFIABLE`
> skip is gone. Five of the six hash computations are now reproducible from the spec; only
> §5.5's `OverrideAuthorizationPayload` remained untested at that point, for want of a fixture
> — since closed by D-023; all six hash computations are now reproducible. The finding's
> substance held: the gap was real and it was the *cause* of the fix. The diagnosis was
> incomplete — the preimage encoding guessed here was substantially correct, and the reason
> nothing matched was that no artifact published the committed set. See the F-3 resolution
> subsection for what the amended §5.4 still leaves open.

§5 currently specifies *field names*. It needs to specify *encodings*. A schema that names
fields but not their wire types is not implementable by an independent party — which is the
exact property the receipt layer exists to demonstrate.

## 1. Findings

**BLOCKER** = cannot implement from the spec. **MAJOR** = two readings produce different
bytes, and the wrong one fails silently or misleads. **MINOR** = friction.

### F-1 — BLOCKER — §5.4 gives no Solidity types, so the EIP-712 type string is unrecoverable

§5.4 lists thirteen bare field names. EIP-712 needs
`typeHash = keccak256("Name(type₁ field₁,…)")`, so the digest depends on the struct name and
the declared Solidity type of every field. §5 supplies neither, and never states which
`EIP712Domain` fields are in use.

**Why guessing fails silently and expensively.** In `abi.encode` every `uintN` occupies one
left-padded 32-byte word. `uint16 schemaVersion` and `uint256 schemaVersion` encode to
*byte-identical data*. The width changes only the type string → typehash → digest →
recovered address. No error, no length mismatch, no diagnostic. The verifier reports "signer
mismatch" and a reasonable operator concludes the receipt is **forged**. A width typo and a
forgery are indistinguishable at the output.

3 struct names × 224 type combinations were enumerated. Exactly one recovered `domain.json`'s
`signerAddress`:

```
DecisionReceiptPayload(uint16 schemaVersion,bytes32 decisionId,bytes32 actionHash,
bytes32 mandateHash,bytes32 policyHash,uint8 verdict,bytes32 reasonCodesHash,
bytes32 evidenceHash,uint256 simulationBlockNumber,bytes32 simulationBlockHash,
uint64 issuedAt,uint64 expiresAt,address signer)
```

The widths are neither guessable nor internally uniform. **The uniform-`uint256`
combination — by far the most conventional guess — is in the set that failed.**

There was a success signal only because `domain.json` publishes `signerAddress`. Without it
there is no oracle: a wrong type string and an invalid signature look identical. **The
samples are verifiable only because of a field that exists for fixture convenience.**

Also undocumented: `signer` is a member of the struct *and* the recovered address. Good
design — a swapped `signer` field fails rather than quietly recovering another key — but §5
doesn't say it's deliberate, so a reimplementer might reasonably exclude it as envelope-like,
by analogy with the rule about signatures.

> **Proposed for §5.4.** The DecisionReceiptPayload is signed under EIP-712 with the domain
> type `EIP712Domain(string name,string version,uint256 chainId,address verifyingContract)`
> (no `salt`), and the struct type string, which is normative and byte-exact: *[string
> above]*. The `signer` field is inside the signed struct: the signature commits to the
> claimed signer rather than merely recovering some address. Implementers are warned that
> `uintN` widths do not change the encoded data — only the type string, and therefore the
> digest. A width mismatch is indistinguishable from an invalid signature.

Apply the same treatment to §5.1, §5.2, §5.3, §5.5.

### F-2 — BLOCKER — §5.1/§5.2/§5.3 don't say the payload hashes are EIP-712 hashStruct values

§5 says nothing about how `mandateHash`, `policyHash`, `actionHash` are computed. §3.2 and
§5.2 say "canonical policy hash" — but §5.6 uses "canonical" to mean RFC 8785, so a reader
could very reasonably conclude these are JCS-then-keccak hashes. **They are not.** Two
separate things had to be guessed: that the algorithm is EIP-712 hashStruct, and all the
Solidity types.

Recovered and confirmed against all five samples:

```
MandatePayload(uint16 schemaVersion,bytes32 mandateId,address principal,address vault,
uint256 chainId,address target,bytes32 targetCodeHash,bytes4 selector,
uint256 maxNativeValueWei,bytes32 purposeKind,bytes32 resourceId,address beneficiary,
uint64 durationSeconds,bool recurringAllowed,uint64 validAfter,uint64 validUntil,
bytes32 policyHash)

PolicyPayload(uint16 schemaVersion,uint32 policyVersion,address vault,uint256 chainId,
uint8 allowedOperation,bytes32 allowedTargetsHash,bytes32 allowedSelectorsHash,
uint256 maxNativeValueWei,uint256 maxAllowanceIncreaseBaseUnits,bytes32 allowedCallGraphHash,
uint64 validAfter,uint64 validUntil,uint8 failureMode)

ActionPayload(uint16 schemaVersion,uint256 chainId,address vault,uint256 actionNonce,
address target,uint256 valueWei,bytes32 dataHash,uint8 operation,bytes32 mandateHash,
bytes32 policyHash,uint64 deadline)
```

Things a reimplementer needs and §5 does not give:

- `selector` is `bytes4`, and `bytesN` is **right**-padded to 32 bytes while `uintN`/`address`
  are **left**-padded. Backwards → wrong mandate hash. §5.1 doesn't say `selector` is 4 bytes
  rather than `bytes32` or a string.
- `policyVersion` is `uint32` while `schemaVersion` is `uint16`. Nothing suggests that.
- `actionNonce` is `uint256` but `deadline` is `uint64`, mirroring the receipt's
  block-number/timestamp split.
- **These are bare `hashStruct` values — no `\x19\x01` prefix, no domain separator.** So
  `mandateHash` is *not* domain-separated. It survives cross-chain/cross-vault confusion only
  because `chainId` and `vault` happen to be struct fields. That should be an asserted
  property, not a coincidence of field choice — especially since §5.5's
  `OverrideAuthorizationPayload` carries **neither** `chainId` nor `vault` and so, if hashed
  the same way, would have no chain binding except through the hashes it references. **This
  could not be tested — no sample exercises §5.5 — but on the §5.1–§5.3 pattern it looks like
  a live gap worth checking before v1.**
  >
  > **RETIRED on evidence, 2026-08-15 (D-023). The binding holds. This concern was wrong.**
  > See the F-2 §5.5 resolution below.
- §5.3's "The complete calldata accompanies the payload" is true: `callData` rides alongside
  and is **excluded** from the struct hash, committed only via `dataHash = keccak256(callData)`.
  §5.3 doesn't say that; a reimplementer including `callData` as a `bytes` member gets a
  different hash.

#### F-2 — §5.5 chain binding: RETIRED on evidence by D-023 (2026-08-15)

*The finding above is preserved as written. This subsection records the measurement.*

**I was wrong, and I am glad to be.** I reasoned that because `OverrideAuthorizationPayload`
carries neither `chainId` nor `vault`, it "would have no chain binding except through the
hashes it references", and flagged it as a likely live gap. §5.8 now publishes the type
string and `case-4-review-failmode-review/override.json` supplies a real owner-signed
override, so I constructed the cross-deployment case instead of reasoning about it.
**The binding holds, by two independent mechanisms, and it is stronger than the original §5.5
text suggested.**

The override verifies end to end: `hashStruct`
`0x2219530e90ec210fb023f8eb8e8210fd401f049c3b4b2fea53b462d094ff8d4e`, digest
`0x13409c770aca097bba9dd7009c7bcbff5fbdd6c253f2cca177ff2ed80d99d8a6`, recovering
`0xf39f…92266` = `ownerAddress` = `mandate.principal` — and *not* the Sentinel signer
`0x7099…79C8`, which is the §3.3(7) property holding in practice. `reviewReceiptHash` equals
the receipt's own EIP-712 `hashStruct`, and `actionHash`/`mandateHash`/`policyHash`/
`actionNonce` all match the receipt and action in that directory.

**The measurement.** I built a synthetic "deployment B" and perturbed one variable at a time,
recording which mechanism notices:

| perturbation | domain separator | referenced hashes |
|---|---|---|
| different `chainId` | catches | catches |
| different vault / `verifyingContract` | catches | catches |
| different domain `name`/`version` | catches | **blind** |
| different mandate, same deployment | **blind** | catches |
| different policy, same deployment | **blind** | catches |
| different `actionNonce` | **blind** | catches |

Both mechanisms fire on every real cross-deployment move, because any distinct deployment
differs in `chainId` or in `verifyingContract` — and in this design `vault` *is* the
`verifyingContract`, so the two mechanisms key on the same two facts from opposite directions.
The untouched, genuinely-signed override lifted to chain 8453 recovers a garbage address, not
the owner.

The last two rows are the part worth keeping: **the mechanisms are genuinely independent, not
redundant restatements.** Changing only the domain `name` leaves every referenced hash
byte-identical and only the separator notices. Substituting a different mandate on the *same*
deployment leaves the separator identical and the signature perfectly valid, and only the
referenced hashes notice. Neither alone is sufficient; together they cover both axes.

**And the sharpest form of the original worry also fails.** `DecisionReceiptPayload` really
does carry no `chainId` and no `vault`, and `reviewReceiptHash` is a hash of exactly that
payload — so my concern had one more level of indirection than I credited. But the receipt
references `actionHash`, `mandateHash` and `policyHash`, and all three of *those* payloads
carry `chainId` and `vault`. Moving the deployment to chain 8453 changes the receipt's
`hashStruct` even though not one of its own fields mentions a chain. The override therefore
references three independently chain-bound hashes at depth one, plus a fourth that is
chain-bound at depth two. That is not a thin binding.

**Tamper coverage added:** substituted `reviewReceiptHash`, incremented `actionNonce`, a
cross-deployment replay, and — the one that actually tests §3.3(7) — a **valid** signature
over the **unmodified** payload produced by the Sentinel signer's key instead of the owner's.
Nothing about that forgery is malformed; only the party is wrong. A flipped byte cannot test
that, so `secp256k1.py` gained a clearly-marked test-only `sign_digest`. All four are
rejected.

**On whether §5.8 is sufficient to build from: yes.** The override was implemented directly
from the published type string, first attempt, no search, no oracle needed. As a control on
the earlier work, all five type strings I had recovered by brute force match §5.8
byte-for-byte; a test now pins the published spec and the implementation together, so a future
edit to either that breaks the agreement fails the suite. The one substantive thing §5.8 still
does not say is **who** signs an override — the type string and §5.5 describe the payload, and
that the owner rather than the Sentinel signer holds the key is inferable from §3.3(7) and
from `ownerSignature`/`ownerAddress` being fixture field names, but §5.8's warning block would
be the natural place to state it outright, alongside the `signer`-inside-the-struct note it
already carries for the receipt. Two smaller gaps: §5.5 says "A block receipt cannot be
overridden" but nothing states that a verifier must *enforce* the target verdict is REVIEW (I
enforce it), and `issuedAt`/`expiresAt` are in the struct with no statement of what a verifier
does when an override is presented outside its window (I do not currently check it, because
"expired" is a vault-side liveness question rather than an artifact-integrity one — but that
is my judgment, not the spec's).

**Value of closing this:** recovering these turned the CLI from "checks the signature and the
evidence hash" into "checks the whole chain". Before it, **a receipt correctly signed over the
wrong mandate would have passed** — exactly the attack a conformance receipt exists to
prevent, undetectable by a spec-conformant verifier.

> **Proposed, after the §5 payload lists.** Every payload hash named in this section
> (`mandateHash`, `policyHash`, `actionHash`, `reviewReceiptHash`) is the EIP-712 `hashStruct`
> of the corresponding payload: `keccak256(typeHash ‖ abi.encode(fields in the order
> listed))`. These are **not** RFC 8785 JSON hashes — RFC 8785 applies only to the
> EvidenceBundle (§5.6) — and they are **not** full EIP-712 digests: no `\x19\x01` prefix and
> no domain separator is applied. Chain and vault binding for these hashes comes solely from
> the `chainId` and `vault` members of the payloads themselves. ActionPayload's accompanying
> `callData` is not a member of the signed struct; it is bound only through
> `dataHash = keccak256(callData)`.

### F-3 — BLOCKER — `reasonCodesHash` is not recomputable by anyone but Sentinel

§5.4 says `reasonCodesHash`. That is the entire specification.

`case-1-allow` has no reason codes and hashes to `keccak256("")`, ruling out any length prefix
or ABI offset. `case-3` has exactly one code, `EVAL_PURCHASE_RESOURCE`, pinning the
per-element encoding with no ordering ambiguity. Against that single value the following were
tested: concatenated `keccak256(code)`; concatenated raw UTF-8; comma-joined; newline-joined;
compact and spaced JSON arrays; right-padded `bytes32` codes; ABI dynamic-array encodings with
and without offset word; length-prefixed; double-keccak; hex-string-of-keccak; lowercased; and
six namespace-prefixed variants. **None matched.**

**Why this matters more than it looks.** Reason codes are the human-facing "why" — the payload
of the whole courtroom-verification claim. The receipt commits to them, so they are *meant* to
be tamper-evident. But no independent verifier can check that commitment. **A receipt signed
over the correct evidence, mandate, policy and action, but carrying a substituted reason-code
set, passes every check any third party can perform.** This is a single-point exception to the
provider-neutrality property D-010 exists to demonstrate.

There is a second coin-flip even given the encoding: in `case-2`, `meta.json` lists the six
codes alphabetically while the bundle's `policyChecks` yields them in evaluation order. Both
are defensible hash inputs; the spec picks neither.

> **Proposed for §5.4** (construction is a *proposal*, not a recovered fact — substitute
> whatever the evaluator actually does, but write it down and make the ordering explicit).
> `reasonCodesHash` is `keccak256(abi.encodePacked(c₁ ‖ … ‖ cₙ))` where each `cᵢ` is the
> 32-byte `keccak256` of the reason code's ASCII identifier, codes in **ascending byte order
> of the identifier** (not evaluation order), deduplicated. The empty list hashes to
> `keccak256("")` = `0xc5d2460186f7233c927e7db2dcc703c0e500b653ca82273b7bfad8045d85a470`. The
> codes bound are exactly the `policyChecks` entries whose `outcome` is not `PASS`.

#### F-3 — RESOLVED by D-022 (2026-08-15). Implemented; the check is now real.

*Everything above is preserved as the original finding. This subsection records the outcome.*

**What I concluded, and what was actually true.** I concluded the preimage was underspecified
*and* unrecoverable. The first half was right and drove the fix. The second half was wrong
about the cause: my guessed construction was, in substance, correct — dedup, ascending byte
order, keccak256 — and one of the encodings I tested was the delimiter-joined form that D-022
ratified. **Nothing matched because the committed set is the union of the evaluator's reason
codes and the isolated signer's own findings, and no shipped artifact published that union.**
I was hashing the evaluator's half against a hash of the whole. That was a fixture gap, not a
reasoning error, but it is worth being precise about what my search could and could not have
found: no amount of brute force over *encodings* recovers a set whose *membership* is not
published. The failure mode was invisible to me — a wrong encoding and a wrong input set both
present as "no candidate matched".

The corrected §5.4 construction: union of evaluator codes and signer findings, de-duplicated,
sorted ascending by identifier bytes, joined with a single `\n`, UTF-8, keccak256; empty set
hashes to `keccak256("")`. Identifiers match `^[A-Za-z0-9_.:-]{1,64}$`, enforced at the
signer's RPC boundary. Verified against all five regenerated samples.

**Now implemented** in `reasoncodes.py`, replacing the `NOT VERIFIABLE` skip with three real
checks: identifier grammar, the hash recomputation, and `signerFindings ⊆ reasonCodes`.
Tamper coverage: substitute, add and remove are rejected; a pure reorder still verifies.

**Three things the amended §5.4 still does not settle** — each was a decision I had to make:

1. **"Union" is a production rule, and reads as a verifier instruction.** §5.4 says the
   committed set *is* the union of two things, but the verifier is handed `reasonCodes`
   already unioned. Taken literally as a verifier instruction — recompute
   `union(reasonCodes, signerFindings)` — the verifier becomes **strictly weaker**: deleting
   any code that also appears in `signerFindings` is silently repaired by the union and goes
   undetected. In the current samples every signer finding is also in `reasonCodes`, so both
   readings produce identical hashes and the corpus cannot distinguish them. I hash the
   published `reasonCodes` and assert the subset relation separately; a regression test pins
   it. **§5.4 should say explicitly which array a verifier hashes.**
2. **The printed pattern does not do what the sentence claims it does.** §5.4 says the
   pattern "is what removes the delimiter and the collation as sources of disagreement". As
   printed, `^[A-Za-z0-9_.:-]{1,64}$`, that is false in two of the three most likely
   implementation languages, because `^`/`$` are not absolute anchors:
   - **Python** (the language D-010 mandates): `re.match(r"^[A-Za-z0-9_.:-]{1,64}$",
     "EVAL_OK\n")` **matches** — `$` matches before a trailing newline. The identifier ends
     in the delimiter.
   - **Ruby**: `^`/`$` are line anchors unconditionally, so `"EVIL\nINJECTED"` **matches**.
   - **JavaScript**: correct, `$` is end-of-input without the `m` flag.

   This is not pedantry — it is a collision. `{"EVIL\nINJECTED"}` and `{"EVIL", "INJECTED"}`
   produce the byte-identical preimage `EVIL\nINJECTED` and therefore the same
   `reasonCodesHash`, so a receipt can commit to two different sets at once. The grammar is
   the *only* thing preventing it, and as written the grammar does not hold. **§5.4 should
   print the rule as absolute anchors and say so:** `\A[A-Za-z0-9_.:-]{1,64}\z`, or in prose
   "the identifier must match end-to-end; implementations must use `fullmatch`/`\A…\z` rather
   than `^…$`, which is a line anchor in some languages." My implementation uses
   `re.fullmatch` and a test asserts the printed pattern's laxity to keep the hazard visible.
3. **Enforcement "at the signer's RPC boundary" is not enforcement at the verifier.** A
   third-party verifier is outside that boundary by construction and must re-validate. §5.4
   should say the verifier MUST reject a non-conforming identifier rather than sanitise it,
   and should state what a verifier does when `reasonCodes` is **absent** — I treat it as a
   verification failure for a signed receipt, on the reading that "a verifier must be given
   it" makes absence a failure to meet the spec, but that is my inference.

**Smaller gaps.** The empty-set rule is redundant but harmless — `"\n".join([])` is `""`, so
the general rule already yields `keccak256("")`. Whether de-duplication is exact-match or
case-folded is unstated; I use exact match, consistent with byte-order sorting. No sample now
has exactly **one** reason code, so the corpus does not pin the "no trailing delimiter" edge —
a producer emitting `code + "\n"` for a single-element set would pass every shipped fixture.
Worth one more fixture.

**What remains unverifiable:** nothing in the reason-code path. F-3 is closed. The residual
limits on this verifier are the ones in §3, none of which are about reason codes.

### F-4 — MAJOR — the verdict enum is unspecified, and the spec's own prose implies the wrong one

Actual mapping, recovered from `index.json`/`meta.json`: **0 = BLOCK, 1 = REVIEW, 2 = ALLOW**.
This is fail-closed ordering (zero = most restrictive). It is the *right* choice.

**But every ordering in the prose implies the opposite.** §4.2 presents Allow, Block, Block,
Review. §5.4 says "The executable allow, block, or review verdict". §5.7 and §11 use the same
allow-first ordering. A reader deriving the enum from the document's own ordering gets
`ALLOW = 0` — precisely inverted on the field §5.4 makes security-critical: "Only an allow
receipt is executable on the automatic path."

**Why MAJOR rather than MINOR: it does not fail loudly.** `verdict` is a `uint8` inside the
signed struct, so the reader's *interpretation* doesn't affect the digest. A verifier with the
enum backwards passes every cryptographic check and then reports the opposite verdict.
Signature valid, evidence hash valid, mandate bound, verdict inverted. That is the worst
possible failure mode for this artifact.

The same unstated convention governs `failureMode` (`0 = FAIL_CLOSED`, `1 = REVIEW`) — again
undocumented, again reversed relative to D-015's amendment text, which mentions REVIEW first.
And `allowedOperation`/`operation` are `0` in all samples with §4 saying "One top-level EVM
operation type: CALL", so `CALL = 0` is inferable but never stated.

> **Proposed.** `verdict` is a `uint8` enum: `BLOCK = 0`, `REVIEW = 1`, `ALLOW = 2`. The
> ordering is deliberate and fail-closed: the zero value is the most restrictive verdict, so an
> uninitialised or truncated field denies rather than permits. Note this is the reverse of the
> order in which §4.2 presents the demonstration cases. `failureMode` is a `uint8` enum on the
> same principle: `FAIL_CLOSED = 0`, `REVIEW = 1`. `allowedOperation` and `operation` are
> `uint8` enums: `CALL = 0`.

### F-5 — MAJOR — §5.6's EvidenceBundle list is incomplete: 12 listed, 15 shipped

Every sample bundle has the twelve listed fields **plus** `schema`
(`"sentinel.evidence.v0.2"`), `verdict` (`"ALLOW"`/`"BLOCK"`/`"REVIEW"`), and `anchor`
(`{blockNumber, blockHash}`).

Because the *entire bundle* is canonicalized and hashed, an omitted field is not cosmetic: a
producer built strictly from §5.6 emits a 12-key bundle whose hash cannot match any receipt
ever issued. §5.6 doesn't say whether its list is exhaustive, minimum, or illustrative.

Three consequences §5 leaves open:

1. **`verdict` is stated twice in two encodings** — the bundle's string vs the receipt's
   `uint8`. Nothing requires them to agree. If they can disagree, the dashboard and the
   executable receipt can tell an operator different stories about the same decision, each
   individually well-formed. The verifier checks it; it has no spec basis to.
2. **`anchor` duplicates the receipt's simulation block.** Same situation, same lack of basis.
3. **`schema` is a version string §5 never mentions**, distinct from payload `schemaVersion`.
   Two independent version axes, one undocumented.

> **Proposed.** Replace §5.6's list with all fifteen fields and add: this list is exhaustive
> and closed. A bundle containing any other member, or missing any listed member, is invalid —
> the whole object is canonicalized, so an extra or absent key changes `evidenceHash`. `schema`
> is the fixed string `sentinel.evidence.v0.2`. `verdict` is the string name of the receipt's
> verdict enum and MUST agree with it. `anchor.blockNumber`/`anchor.blockHash` MUST equal the
> receipt's `simulationBlockNumber`/`simulationBlockHash`. A verifier MUST reject a pair
> violating either agreement.

### F-6 — MAJOR — numbers are strings and §5.6 doesn't say so; the corpus tests none of RFC 8785's hard part

Every numeric value in every bundle is a JSON *string*. §5 never states this.

The reason is sound and belongs in the spec: RFC 8785 §3.2.2.3 mandates ECMAScript
`Number::toString` (IEEE-754 double) serialization. A `uint256` max carried as a bare JSON
number canonicalizes to `1.157920892373162e+77` — silently and irrecoverably. Strings are
**mandatory**, not stylistic.

**The bigger problem: the corpus proves almost nothing about JCS agreement.**

- **Zero JSON numbers appear in any of the five bundles.** The samples exercise *none* of RFC
  8785's number algorithm — by a wide margin its most error-prone part. The canonicalizer here
  reproduces all five byte-for-byte, and **that is essentially no evidence that its number
  handling agrees with the evaluator's.** This one is pinned against the RFC's own vectors; the
  evaluator's may or may not be correct and this corpus cannot tell anyone.
- **Every byte in every bundle is ASCII.** So the UTF-16 code-unit key-sorting rule (§3.2.3)
  and the emit-non-ASCII-literally rule (§3.2.2.2) are equally untested. The sorting rule is a
  genuine trap: `U+FFFD` is one UTF-16 code unit while `U+1F600` is the surrogate pair
  `0xD83D 0xDE00`, so the astral character sorts **first** by code unit and **last** by code
  point. An implementation sorting keys by code point — the obvious thing in most languages,
  and what Python's default `sorted()` does — produces a different hash and **passes all five
  fixtures**.
- `aiExplanation` is free-form model output, `null` in all five samples. It is precisely the
  field most likely to carry an em dash, smart quote, emoji, or CJK text. The first bundle that
  does is the first real test of the JCS layer, and it will happen in the field rather than in
  the fixture set.

> **Proposed for §5.6.** All integer values are encoded as decimal **strings**, never JSON
> numbers. This is required, not stylistic: RFC 8785 §3.2.2.3 mandates IEEE-754 double
> serialization, under which a `uint256` silently loses precision. JSON numbers are therefore
> **forbidden** anywhere in an EvidenceBundle; a bundle containing one is invalid.
>
> **Also for §7.1:** add at minimum one fixture with non-ASCII in `aiExplanation` — including
> one astral-plane character and one BMP character above `U+E000` in the *same* object's keys —
> so a JCS implementation that sorts by code point is caught by the corpus rather than in
> production.

### F-7 — MAJOR — "keccak256" doesn't say *which* keccak, and the wrong one is the stdlib default

§5.6 and §9 say "keccak256" without saying it is the EVM's — original Keccak `pad10*1` with
domain byte `0x01` — rather than FIPS-202 SHA3-256 (`0x06`). Different functions, identical
output length, no distinguishing failure mode.

This is a live trap specifically for the Python reimplementation D-010 mandates: Python's
stdlib ships `hashlib.sha3_256` and no keccak. It is the obvious reach, produces a plausible
32-byte digest for every input, and is wrong for all of them. Obvious to anyone in EVM; the
spec is meant to be implementable by someone who isn't.

> **Proposed.** "…and keccak256 — specifically the EVM's keccak256, i.e. original Keccak with
> `pad10*1` domain byte `0x01`, **not** FIPS-202 SHA3-256 (`0x06`). The two produce different
> digests for every input. Implementations must not use a standard-library `sha3_256`."

### F-8 — MAJOR — the evidence-hash preimage is never pinned; the trailing-newline trap is one keystroke wide

§5.6 never states that the preimage is *exactly* the canonical bytes: no length prefix, no
domain tag, no trailing newline. `evidence.canonical.json` has **no** trailing newline; hashing
it with one yields a completely different digest. Nothing in §5 says which.

This is the cheapest way to break the entire corpus by accident. `jq -c` appends a newline.
`json.dump(...)` plus a habitual `f.write("\n")` appends one. Most editors append on save, and
a `.gitattributes` or formatter can add one to a committed fixture without anyone touching the
file. Any of those silently invalidates every receipt in the repo, and presents as "the
signature is bad".

Smaller: `evidence.hash` contains bare lowercase hex with **no** `0x` and **no** newline. §5
doesn't describe the artifact layout at all.

> **Proposed for §5.6.** `evidenceHash = keccak256(C)` where `C` is exactly the RFC 8785
> canonical UTF-8 byte sequence of the bundle: no BOM, no length prefix, no domain-separation
> tag, and **no trailing newline**. Tooling that appends a trailing newline when writing the
> canonical form (`jq -c`, most editors on save, many `write` idioms) invalidates the hash. The
> canonical form is bytes, not text, and must be written in binary mode.

### F-9 — MAJOR — a receipt is not self-describing, and §5 never says where the domain comes from

`MandatePayload`, `PolicyPayload` and `ActionPayload` all carry `chainId` and `vault`.
`DecisionReceiptPayload` carries **neither**. A Sentinel receipt cannot be verified from the
receipt alone — chain and contract binding lives entirely in the EIP-712 domain separator,
external to the artifact.

Defensible (it is what domain separation is *for*), but it has an operational consequence §5
doesn't address: **a third party handed a receipt has no way to know which domain to verify
against.** In the fixtures this is solved by `domain.json`, explicitly a fixture convenience.
In the field there is nothing.

> **Proposed for §5.4.** Unlike §5.1–§5.3, the DecisionReceiptPayload does not carry `chainId`
> or `vault`; its chain and contract binding exists solely in the EIP-712 domain separator. A
> deployment MUST therefore publish its domain field values and the resulting `domainSeparator`
> alongside the SentinelVault address, and a receipt transmitted outside the lab MUST be
> accompanied by them. A verifier not told the domain cannot verify a receipt, and one that
> guesses will report a valid receipt as forged.

### F-10 — MINOR — the signature envelope encoding is unstated

§5.4 says only "sentinelSignature". Not stated: 65-byte `r‖s‖v` vs `v‖r‖s`; `v ∈ {27,28}` vs
`{0,1}`; whether EIP-2 low-`s` is required; whether EIP-2098 compact signatures are accepted.
All five samples are 65-byte `r‖s‖v`, `v ∈ {27,28}`, low-`s`, `0x`-prefixed lowercase.

> **Proposed.** "`sentinelSignature` is 65 bytes, `r ‖ s ‖ v`, hex-encoded with a `0x` prefix,
> `v ∈ {27, 28}`, and MUST be EIP-2 canonical (`s ≤ n/2`). EIP-2098 compact signatures are not
> accepted."

### F-11 — MINOR — address casing is inconsistent across the fixtures and unspecified

`receipt.signer` and `domain.verifyingContract` are lowercase; `domain.signerAddress` is EIP-55
checksummed. §5 says nothing. A verifier comparing `receipt.signer == domain.signerAddress` as
strings fails on **all five samples**.

> **Proposed.** State that addresses compare case-insensitively and EIP-55 casing is
> display-only; make the fixture set internally consistent.

### F-12 — MINOR — `schemaVersion` has no defined semantics, which matters *because* it is inside the signed struct

All payloads carry `schemaVersion: "1"`; bundles carry `schema: "sentinel.evidence.v0.2"`. §5
never says what increments a version, whether a verifier must reject unknown versions, or — the
load-bearing question — **whether the EIP-712 type string is version-dependent.** Decide and
write it now, while exactly one version exists and the decision is free.

> **Proposed.** "`schemaVersion` selects the EIP-712 type string. A verifier MUST reject a
> payload whose `schemaVersion` it does not have a type string for, rather than attempting the
> latest. §5 will carry one type string per version indefinitely; type strings are never
> revised in place."

### F-13 — MINOR — `refused: true` is specified nowhere and exercised by no sample

None of the five samples carry `refused: true` — all are `"refused": false`. And §5.4 describes
`SignedDecisionReceipt` as "DecisionReceiptPayload plus sentinelSignature" with no refusal
envelope at all. The shape is both undocumented and untested.

Open questions §5 doesn't answer: is `receipt` `null`, absent, or partial when refused? **Is a
refusal signed?** If not, anyone can forge one — for a fail-closed system arguably acceptable,
but it should be a recorded decision rather than an accident, since a forged refusal is a
denial-of-service on a legitimate action. Is `refused: true` alongside a populated signed
receipt legal? Is there a reason field, and is it bound to anything?

**What was implemented, all guesswork:** evidence checks still run in full; receipt-bound checks
report SKIP with the reason; `refused: true` *with* a receipt body is a hard FAIL as
self-contradictory. Tests synthesise all three shapes since no fixture does.

> **Proposed.** Specify the refusal envelope in §5.4, decide explicitly whether refusals are
> signed, add a refusal fixture to §7.1.

## 2. What was got wrong, and what corrected it

1. **Uniform `uint256` for the receipt's integer fields** — the conventional choice, and wrong;
   the real type string mixes `uint16`/`uint8`/`uint64`/`uint256`. Corrected only because
   `domain.json` publishes `signerAddress`, giving the search a success oracle. With no oracle
   there is no way to distinguish a wrong type string from a bad signature. This is F-1 and the
   single most expensive gap in §5.
2. **Verdict enum from the document's own ordering** — §4.2 presents allow-first, yielding
   `ALLOW = 0`. Truth is `ALLOW = 2`. Corrected by `index.json`/`meta.json`, artifacts that
   exist for the fixture harness rather than for verification. Nothing in §5 would have caught
   it, and neither would the cryptography.
3. **Treating §5.6's twelve fields as the complete bundle** — it is fifteen. Caught only because
   verification ran against shipped canonical bytes; a producer built from §5.6 would ship a
   bundle nothing could verify.
4. **Assuming the payload hashes were JCS-then-keccak** — §5's use of "canonical" for both the
   bundle (RFC 8785) and the policy hash (EIP-712 hashStruct) pushed the wrong way.
5. **An evidence-only tamper test** — the first `--tamper` mode mutated the bundle and correctly
   failed, but the signature checks still passed. That exposed that a single-mode tamper test
   never exercises the signature path. The shipped self-test now runs three modes and requires
   all three rejected, plus wrong-domain, wrong-`verifyingContract`, and swapped-mandate tests.
6. **Hazards avoided but which remain spec gaps**, listed because the next implementer may not:
   `hashlib.sha3_256` (F-7), a trailing newline on canonical bytes (F-8), sorting JCS keys by
   code point (F-6), and right- vs left-padding for `bytes4 selector` (F-2).

## 3. What this verifier does *not* prove

- ~~**`reasonCodesHash` is unchecked** (F-3) — reason codes are not tamper-evident to any
  third party.~~ **Superseded by D-022 (2026-08-15):** §5.4 now defines the construction,
  the samples publish `reasonCodes`, and the check is implemented. Reason codes are
  tamper-evident. See the F-3 resolution subsection.
- ~~**§5.5 `OverrideAuthorizationPayload` is entirely unexercised.**~~ **Superseded by
  D-023 (2026-08-15):** §5.8 publishes its type string, a signed override fixture exists,
  and it verifies end to end with four tamper modes rejected. The chain-binding concern
  raised in F-2 was measured and **retired** — see the F-2 §5.5 resolution.
- **RFC 8785's number and non-ASCII paths are unexercised by the corpus** (F-6) — this
  implementation is pinned to the RFC's vectors; agreement with the *evaluator* on those paths
  is untested by anything, because no fixture reaches them.
- **The bundle's factual content is not checked against a chain** — this confirms the bundle is
  the one the receipt commits to and that the receipt is correctly signed. It cannot confirm
  `observedPreState`, `nativeBalanceDeltas` or `targetCodeIdentity` reflect what happened on
  chain; that needs an archive node at the anchored block. **Verifying a receipt is not
  verifying the simulation.**
- **`decisionId` is unverified** — §5.4 never says how it is derived.
- **Signer authorisation is out of scope** — the CLI confirms the signature recovers the address
  `domain.json` names; whether that is the vault's *currently active* signer is on-chain state
  this tool does not read.

## 4. Priority for §5 revision

If only three things are fixed:

1. **F-1 / F-2 — publish every EIP-712 type string verbatim.** Without them §5 is not
   implementable, which defeats the receipt layer's provider-neutrality claim.
2. ~~**F-3 — define `reasonCodesHash`.**~~ **DONE — D-022, 2026-08-15.** Implemented and
   verified against all five samples. Three residual wording gaps are recorded in the F-3
   resolution subsection; the anchor-semantics one (item 2) is a real collision risk and
   should be fixed before the gate.
3. **F-4 — state the verdict enum.** The one error that passes every cryptographic check and
   still reports the opposite answer.

F-6's fixture additions are the cheapest real increase in corpus strength available; F-8's
trailing-newline sentence is one line that prevents a class of accidental corpus-wide breakage.

## 5. Reproduction

```sh
python3 verifier/verify.py fixtures/samples/case-1-allow   # one sample, verbose
python3 verifier/verify.py --all fixtures/samples          # all five
python3 verifier/verify.py --tamper --all fixtures/samples # negative self-test
python3 verifier/verify.py --print-types                   # the recovered type strings
python3 verifier/test_verifier.py                          # test suite
```

**Results at time of writing (2026-08-15):** 5/5 samples PASS · 15/15 tamper cases rejected ·
39/39 tests OK. Per sample, 16 checks pass and 1 (`reasonCodesHash`) reports NOT VERIFIABLE.

**Results after D-022 (2026-08-15):** 5/5 samples PASS · 32/32 applicable tamper cases behave
as specified · 55/55 tests OK. Per sample, 18-19 checks pass and none report NOT VERIFIABLE.
The tamper suite gained four reason-code modes; three of the 35 mode/sample combinations are
N/A because `case-1-allow` has an empty reason-code list, and `reasons-reorder` is a control
that must *still verify* rather than be rejected.

**Results after D-023 (2026-08-15):** 5/5 samples PASS · 36/36 applicable tamper cases behave
as specified · 70/70 tests OK. The override sample runs 11 additional checks. All six §5.8
type strings are exercised; none of the six hash computations is unverifiable.
