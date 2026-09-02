#!/usr/bin/env python3
"""Fail-closed verifier for the Sentinel v0.3 publication bundle.

The caller supplies a deployment authority address obtained independently of the
publication material.  That authority signs the deployment manifest, and the
manifest then supplies the chain, vault, owner and signer that every EIP-712
artifact must match.  The presenter has no way to nominate the deployment
identity: `deployment.py` enforces a closed field set, so a manifest naming its
own trust root is refused, and authority reaches this tool only through the
caller's argument.

WHAT A PASS FROM THIS TOOL MEANS, AND WHAT IT DOES NOT (D-087(c), 2026-09-01)
----------------------------------------------------------------------------
This verifier certifies EXECUTABILITY, statically and offline: whether
SentinelVault's offline-checkable action predicate accepts this bundle at the
entry point it is presented for -- the verdict, a §5.5 owner override wherever
one is required or present, every validity window, and the action's target,
value, selector and operation against the signed mandate and policy -- plus the
content arms ported under D-087 (§5.6 projections, §5.4 reason codes, §5.7.1
signer-attested conformance).  A REVIEW receipt with no override and a BLOCK
receipt are both refused here, because the Vault executes neither.

It is NOT the authenticity verifier.  verifier/verify.py (not shipped in the
release tree) certifies AUTHENTICITY -- that the bundle is genuinely what the
named signer produced -- and finds both of those bundles authentic, as it
does a §5.5.1 refusal record; since D-090(a) and D-091(a) it reports each of
the three as `=> AUTHENTIC, NOT EXECUTABLE` with exit status 3 rather than as
a PASS, so that its exit code does not say "pass" to a script for anything
the Vault would not execute.  `=> PASS: AUTHENTIC` from verify.py (ALLOW,
or REVIEW with a valid owner override) and `PASS (static, offline)` from this
tool remain two different claims that used to share one word; the split is
deliberate, was ruled at D-087(c), and is stated on both surfaces so that
neither is read as the other.

"Executability" here is the Vault's OFFLINE-CHECKABLE predicate and nothing
more.  Whether the Vault would execute this bundle at any actual block also
turns on state this tool cannot read -- the nonce, pause, mandate and policy
activation, deployed code, and the three §4 backstops -- so executability ON
CHAIN is among the things listed as NOT ESTABLISHED beside every result.

WHAT A RUN OF THIS TOOL DOES NOT ESTABLISH
------------------------------------------
Recorded here, in the text argparse reprints under --help, because this docstring
previously claimed the opposite of the third item.

* NO CHAIN IS READ, SO DEPLOYMENT IDENTITY IS NOT ESTABLISHED.  `runtimeCodeHash`,
  `deploymentBlockHash` and `compilerMetadataHash` are authenticated as things the
  deployment authority SAID.  They are compared against no deployed bytecode and
  no state proof, so this tool cannot tell you the described code is what is
  deployed (R-A018-04).  D-086(e) ruled the non-certifying-static route: the
  result carries those values only under a key that says they are unverified
  authority assertions, never as bare facts beside the verdict, and the headline
  never claims an authenticated deployment.  Live RPC is NOT AUTHORISED.
* NONCE FRESHNESS CANNOT BE ESTABLISHED OFFLINE.  Only the Vault consumes an
  action nonce, atomically, at execution.  An offline verifier can at best
  observe nonce state at an authenticated block, and this one observes none
  (R-A018-02).
* THERE IS NO TRUSTED CLOCK, SO CURRENTNESS AT A BLOCK IS NOT ESTABLISHED.
  Validity windows are evaluated against the host clock, which is not an
  authenticated block timestamp.  `--evaluation-time` moves that choice from the
  machine running the check to whoever writes the command line, so a run under
  that flag reports its findings and then refuses to certify anything at all
  (R-A018-03).
* THE VAULT'S THREE §4 HARD BACKSTOPS ARE NOT READ.  After the mandate's and
  policy's copies have passed, SentinelVault still refuses `ValueOverCap`
  against its own immutable `maxNativeValueWei`, `TargetNotAllowed` against the
  owner-set `allowedTarget` allowlist and `SelectorNotAllowed` against
  `allowedSelector`.  All three are Vault state this tool cannot reach, and a
  bundle the mandate admits may still revert on them (D-087(a)).
* THE CALLDATA ARGUMENTS ARE NEVER DECODED.  `action.callData` is bound by
  `dataHash` to the bytes presented, and its leading four bytes are compared to
  the mandated selector -- but nothing after that selector is decoded, so a
  beneficiary, recipient or amount encoded inside the calldata is compared to no
  mandated value BY THIS TOOL'S OWN DECODING.  A bundle in which only the
  beneficiary word was rewritten is internally consistent and authenticates
  here.  Only the isolated signer's evaluator decodes those arguments; the
  Vault, like this tool, binds the bytes.  RULED DISCLOSED-ONLY, not deferred:
  D-083(b) settled that this tool decodes nothing (R-A018-17).  The cost
  recorded with that ruling -- "no independent downstream check" -- was
  CORRECTED on 2026-08-31: the check below compares the signer's ATTESTED
  record, so there is a downstream check, and it is weaker than decoding.
* THE SIGNER-ATTESTED RECORD IS THE SIGNER'S OWN WORD.  The §5.7.1 check named
  "signer-attested record conforms to mandate" (D-087(b)) compares the decoded
  record the signer attested inside `evidence.json` -- `resourceId`,
  `beneficiary`, `durationSeconds`, `recurringAllowed`, `spender`, the
  allowance ceiling -- against the mandate, without decoding calldata.  It
  catches a misconfigured-but-honest evaluator that reported what it decoded
  and said ALLOW anyway.  It honestly does not catch a lying signer, because
  the record it reads is the signer's.  It is never named as a verification of
  the beneficiary, because that would be true only of an honest signer.

EXECUTION PATHS
---------------
`SentinelVault.sol` has exactly two entry points and deliberately no third.
`executeWithReceipt` reverts `NotAllowVerdict` on anything that is not ALLOW;
`executeWithOverride` reverts `NotReviewVerdict` on anything that is not REVIEW
and additionally requires a separate owner-signed override naming that exact
receipt, action and nonce.  This verifier mirrors that split: the caller declares
which entry point the bundle is presented for with --execution-path, and a BLOCK
receipt is executable through neither.

`SentinelVault.sol:357` also reverts `UnsupportedOperation` on any
`action.operation` other than CALL, UNCONDITIONALLY -- no policy field can
enable DELEGATECALL or CREATE -- and this verifier refuses the same way, before
and regardless of `policy.allowedOperation` (D-087(a)).

A BUNDLE'S §5.5 CREDENTIAL IS EXAMINED ON WHICHEVER PATH IT IS PRESENTED FOR, not
only on the one that could use it (R-A018-18, ruled at D-083(c)).  An `override.json`
sitting beside an ALLOW receipt is refused rather than passed over: a credential no
Vault entry point will accept must not ride inside a PASS unopened, because a run
that never reads it certifies it by omission.

A §5.5.1 SIGNED REFUSAL RECORD IS RECOGNISED AND REFUSED, NOT VERIFIED (D-087(d)).
A refusal is executable at neither entry point, so there is nothing here to
certify about it; verify.py is the tool that authenticates a refusal record.
This tool detects the §5.5.1 shape -- in `refusal.json`, or in `receipt.json`
under `refusalRecord` / `refusal` / `record`, or as `refused: true` -- and
refuses naming what it found, rather than reporting "missing required artifact
receipt.json", which named the wrong artifact.

THE CONTENT ARMS (D-087(a)/(b), ported from verify.py on 2026-09-01)
--------------------------------------------------------------------
Until this batch the tool authenticated that `evidence.json` was THE bundle the
signer signed over and never that it DESCRIBED THIS ACTION: the artifact a
recipient actually reads could be replaced wholesale with `{"note": ...}`,
re-hashed and re-signed, and still certify.  Now, on every certifying path:
`evidence.normalizedAction` must restate the §5.3 action field by field and its
`callData` must hash to `action.dataHash`; `evidence.verdict` must agree with the
signed receipt; `evidence.anchor` must name the receipt's simulation block;
`evidence.expectedEffects` must project the signed mandate and policy with the
native ceiling INTERSECTED (§5.2); the published `reasonCodes` list must hash to
the receipt's `reasonCodesHash` under §5.4's own construction and contain every
`signerFindings` entry; and, under ALLOW only, the signer-attested record must
conform to the mandate (§5.7.1).  BLOCK and REVIEW bundles are legitimately
nonconforming -- that is what they are for -- so the last check binds to ALLOW,
as verify.py's does.

EXIT CODES
----------
Listed here, not only in the `--help` text, because a caller wiring this tool
into a script reads the module or the release documentation rather than running
`--help` -- and a third code that only one of those three surfaces mentions is a
code somebody's `if status != 0` will silently mistreat as a refusal.

* **0** -- CERTIFYING.  Static offline executability established, with the
  `NOT ESTABLISHED` list above still outstanding.
* **1** -- REFUSED.  A check failed; the reason is printed to stderr as `FAIL:`.
* **3** -- NOT CERTIFIED, and not a refusal either.  Emitted only under
  `--evaluation-time`, whose findings are the caller's frame rather than an
  observed one (R-A018-03).  A run under that flag reports diagnostics and
  certifies nothing, so treating 3 as either a pass or a failure misreads it.
"""

import argparse
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import deployment
import eip712
import jcs
import reasoncodes
import refusal
from keccak import keccak256
from secp256k1 import RecoveryError, is_low_s, parse_signature, recover_address


# -----------------------------------------------------------------------------
# KNOWN RED TESTS IN THE FROZEN CONTRACT, RECORDED SO THEY ARE NOT SILENT
# -----------------------------------------------------------------------------
# `verifier/test_publication_verifier.py` was written by an independent author who
# was forbidden to edit this module (D-058(1), A-028), and it is not editable from
# this side either -- so work this module deliberately does not do cannot be marked
# `expectedFailure` in the suite and has to be declared here instead. EXACTLY ONE
# of its 105 tests is RED ON PURPOSE. A green count of 104/105 is the expected
# state; 105/105 would mean somebody implemented work that John has ruled out.
#
# `verifier/test_publication_override.py` HAS NO DELIBERATE REDS. 61/61 green is its
# expected state, as of the R-A018-18 repair ruled at D-083(c). A red in that file
# is a regression.
#
# `verifier/test_publication_conformance.py` HAS NO DELIBERATE REDS. 53/53 green is
# its expected state, as of the D-087(a)/(b) content-arm port. A red there is a
# regression of a ported check.
#
#   R-A018-17 (RULED disclosed-only by John at D-083(b). PERMANENTLY RED BY RULING --
#              not pending, not deferred, and not a scope question still open.)
#     TestExactActionIsEnforced.test_calldata_redirecting_the_mandated_beneficiary_is_refused
#     Turning it green would mean decoding calldata against the mandated selector
#     inside this verifier, and D-083(b) ruled that this verifier decodes nothing:
#     the isolated signer's evaluator decodes semantics, the Vault binds bytes, and
#     this tool says plainly that it binds bytes too. D-087(b) did NOT reverse this:
#     the §5.7.1 check it added compares the signer's ATTESTED record, and the test
#     above rewrites the calldata word while leaving the attested record honest --
#     exactly the lying-signer case the attested-record check is documented not to
#     catch. See check_attested_record_conforms_to_mandate() and the R-A018-17
#     entry in NOT_ESTABLISHED, which is how a recipient is told.
#
#   R-A018-04 -- THE THREE FORMER REDS WERE REDEFINED UNDER D-086(e), NOT CLOSED BY
#   CHAIN BINDING. This block used to declare three deferred reds in
#   TestDeploymentIdentityIsNotBound, each asserting a chain binding: that a
#   fabricated runtimeCodeHash is refused, that two contradictory manifests cannot
#   both certify, and that the result names the block its claims are true at.
#   Crucible Cycle 1 Binding Critical 2 bound the CLAIM, not the binding, and John
#   ruled at D-086(e) that Critical 2 is closed by the non-certifying-static route
#   with live RPC NOT AUTHORISED. The contract's author redefined each test to
#   observe the ruled semantic -- the value is never presented as a fact, both
#   contradictory manifests certify STATICALLY and neither claims identity, no
#   block is anchored and executability is named as not established -- and they
#   are green here for that reason. NO CHAIN BINDING EXISTS. `runtimeCodeHash` is
#   still compared to nothing; it now travels under `unverifiedAuthorityAssertions`
#   in the result instead of beside the verdict. When a chain binding is authorised
#   it needs NEW tests -- these three no longer test for one, and a run that
#   refused one of two contradictory manifests would fail the redefined contract.


class VerificationError(ValueError):
    pass


# SentinelTypes.sol: enum Verdict { BLOCK, REVIEW, ALLOW }.
BLOCK, REVIEW, ALLOW = 0, 1, 2
VERDICT_NAMES = {BLOCK: "BLOCK", REVIEW: "REVIEW", ALLOW: "ALLOW"}

# SentinelTypes.sol: enum Operation { CALL, DELEGATECALL, CREATE }. Only CALL
# executes; `SentinelVault.sol:357` reverts UnsupportedOperation on the others
# unconditionally, and so does check_exact_action().
CALL_OPERATION = 0

AUTOMATIC_PATH = "automatic"
OVERRIDE_PATH = "owner-override"

# D-087(b), verbatim. The one name the §5.7.1 check goes by on every surface.
# Never "beneficiary verified": that would be true only of an honest signer.
CONFORMANCE_CHECK_NAME = "signer-attested record conforms to mandate"

# The §5.6 `expectedEffects` fields that are copies of the mandate.
# `maxAllowanceIncreaseBaseUnits` is copied from the policy and
# `maxNativeValueWei` is the §5.2 intersection; both are handled separately.
EXPECTED_EFFECTS_FROM_MANDATE = (
    "target", "selector", "resourceId", "beneficiary", "durationSeconds", "recurringAllowed",
)

# Where a §5.5.1 SignedRefusalRecord may travel inside receipt.json, matching
# `verify.py::_REFUSAL_NESTED_KEYS`. Recognition is by SHAPE and nothing else.
REFUSAL_ENVELOPE_KEYS = ("refusalRecord", "refusal", "record")

# `verify()` reports which of these it produced; `main()` maps them to exit
# codes.  Neither mode certifies executability ON CHAIN -- see the module
# docstring; the static mode certifies the Vault's offline-checkable predicate.
MODE_STATIC = "offline-static-executability"
MODE_DIAGNOSTIC = "non-certifying-diagnostic"

NOT_ESTABLISHED = (
    "deployment identity (live code identity): no chain was read and no state proof was "
    "checked, so the manifest's runtimeCodeHash is authenticated only as an authority "
    "assertion, never as what is deployed (R-A018-04; D-086(e) non-certifying-static route)",
    "nonce freshness: only the Vault consumes an action nonce, atomically, at execution; "
    "an offline run cannot establish that this nonce is unspent (R-A018-02)",
    "a trusted time source: the validity windows below were evaluated against a clock this "
    "tool does not authenticate, not an authenticated block timestamp (R-A018-03)",
    "currentness at a block: because the clock is unauthenticated, the receipt's, mandate's, "
    "policy's, deadline's and override's currency at any actual block is not established; "
    "what is established is that each window contains the evaluation instant reported below",
    "executability on chain: this run certifies only the Vault's offline-checkable action "
    "predicate (verdict, override, windows, target, value, selector, operation). Whether "
    "SentinelVault would execute this bundle at any actual block also depends on state it "
    "did not read -- the nonce, pause, mandate and policy activation, deployed code -- so "
    "executability at a live block is not established (D-086(e))",
    "the Vault's three §4 hard backstops: SentinelVault refuses ValueOverCap against its own "
    "immutable maxNativeValueWei, TargetNotAllowed against the owner-set allowedTarget "
    "allowlist and SelectorNotAllowed against allowedSelector, AFTER the mandate's and "
    "policy's copies of each have passed. All three are Vault state this tool cannot read; "
    "the maxNativeValueWei compared above is the mandate's and the policy's, not the "
    "Vault's (D-087(a))",
    # R-A018-17, and it is the reason the headline below enumerates the four
    # fields it compared instead of saying "the action matches the mandate".
    # `check_exact_action` compares target, valueWei, the leading selector and
    # operation; the ARGUMENTS after that selector are bound by `dataHash` to the
    # bytes presented and to nothing else.  A bundle in which only the beneficiary
    # word inside `callData` was rewritten is internally perfect, and every
    # downstream consumer is likewise byte-binding: the Vault hashes `callData`
    # and never decodes it either.
    #
    # WHETHER THE VERIFIER SHOULD DECODE IS NO LONGER OPEN.  D-083(b) ruled it
    # DISCLOSED-ONLY: the signer's evaluator decodes semantics, the Vault binds
    # bytes, and this tool binds bytes and says so.  The cost recorded with that
    # ruling -- "no independent downstream check" -- was CORRECTED 2026-08-31 and
    # D-087(b) then ported the check verify.py had all along: the signer's
    # ATTESTED record is compared to the mandate (next entry). That is a
    # downstream check, and it is weaker than decoding, and both facts are said.
    "conformance of the CALLDATA ARGUMENTS: the bytes are bound by dataHash and their "
    "leading selector is compared to the mandate, but nothing here decodes them, so a "
    "beneficiary, recipient or amount encoded inside callData is compared to no mandated "
    "value by this tool's own decoding. Only the isolated signer's evaluator decodes them "
    "(R-A018-17, ruled disclosed-only at D-083(b)); what this tool re-checks is the "
    "signer's attested record of that decoding, next",
    "honesty of the signer-attested record: the §5.7.1 check \"" + CONFORMANCE_CHECK_NAME
    + "\" compares the decoded record the signer itself attested in evidence.json to the "
    "mandate, so it catches a misconfigured-but-honest evaluator and does not catch a lying "
    "signer -- a signer that misreports what it decoded passes it (D-087(b))",
)


def read_bytes(path):
    with open(path, "rb") as handle:
        return handle.read()


def read_json(path):
    return jcs.parse_bytes(read_bytes(path))


def required(sample, name):
    path = os.path.join(sample, name)
    if not os.path.isfile(path):
        raise VerificationError(f"missing required artifact {name}")
    return path


def hx(raw):
    return "0x" + raw.hex()


def eq(label, actual, expected):
    if str(actual).lower() != str(expected).lower():
        raise VerificationError(f"{label}: {actual!r} != {expected!r}")


def same(actual, expected):
    """Case-insensitive on strings (hex and addresses), exact on everything else.

    `verify.py::_norm_hex`, restated: a projection that spells an address in
    checksum case is the same projection, and a boolean is compared as one.
    """
    if isinstance(actual, str) and isinstance(expected, str):
        return actual.lower() == expected.lower()
    return actual == expected


def check_signature_form(label, signature):
    """Hold a bundle signature to EIP-2 low-s with v in {27, 28}.

    `verify.py` applies this rule to the receipt, the refusal record and the owner
    override; there is no basis for one rule on those and none on these
    (R-A018-16(a)).  `(r, n-s, v^1)` recovers the same signer, so without the
    check one authorization has two byte-distinct valid forms and any consumer
    keyed on signature bytes sees two authorizations where one party signed once.
    """
    if not isinstance(signature, str):
        raise VerificationError(f"{label} must be a 0x-prefixed string")
    try:
        _, s_value, v_value = parse_signature(signature)
    except (RecoveryError, ValueError) as exc:
        raise VerificationError(f"{label} is malformed: {exc}") from exc
    if v_value not in (27, 28):
        raise VerificationError(
            f"{label} has v={v_value}; EIP-712 signatures carry v in {{27, 28}}"
        )
    if not is_low_s(s_value):
        raise VerificationError(
            f"{label} is not EIP-2 canonical (high-s). The reflected form (r, n-s, v^1) "
            f"recovers the same address, so the authorization is malleable: two "
            f"byte-distinct documents, one decision, and no unique identity for either"
        )


def refusal_presentation(sample, receipt_doc):
    """How, if at all, this bundle presents a §5.5.1 SignedRefusalRecord.

    Returns a phrase naming the presentation, or None for a decision bundle.
    Recognition is by SHAPE ONLY -- the record's digest, signature, charset and
    bindings are deliberately not examined (D-087(d): recognise and refuse, do
    not verify), so a refusal record whose signature is garbage is still
    recognised as a refusal record and refused as one.

    The shapes are `verify.py::_locate_refusal`'s: the record in its own
    `refusal.json`; or inside `receipt.json` under one of the envelope keys; or
    the nine §5.5.1 fields flat where a `receipt` member would be; or the
    harness's bare `refused: true` claim, which §5.5.1 says is an unsigned
    claim of refusal and not a record -- but it is still a bundle presenting a
    refusal, not a decision, and it is named as such rather than as a missing
    receipt.  `refused: false` and an absent key are what a decision bundle
    carries and are not a refusal (the corpus ALLOW bundle ships `refused:
    false`), so presence of the key alone decides nothing.
    """
    if os.path.isfile(os.path.join(sample, "refusal.json")):
        return "refusal.json is present"
    if not isinstance(receipt_doc, dict):
        return None
    envelopes = [key for key in REFUSAL_ENVELOPE_KEYS
                 if isinstance(receipt_doc.get(key), dict)]
    if envelopes:
        return f"receipt.json carries a refusal record under `{envelopes[0]}`"
    if receipt_doc.get("refused") is True:
        return "receipt.json claims `refused: true`"
    if "receipt" not in receipt_doc and any(
            name in receipt_doc for name in refusal.FIELD_NAMES):
        return "receipt.json carries §5.5.1 RefusalRecord fields where a receipt would be"
    return None


def check_not_a_refusal_record(sample, receipt_doc):
    """D-087(d).  A §5.5.1 SignedRefusalRecord is recognised and refused, honestly.

    This tool certifies executability, and a refusal is executable at neither
    Vault entry point, so there is nothing here to certify about one -- and the
    32-check verification arm `verify.py` carries was ruled NOT ported.  What
    was wrong before this function existed was the diagnosis: a refusal bundle
    was refused with "missing required artifact receipt.json" or "receipt.json
    must carry a signed decision receipt" -- both true, both naming the wrong
    artifact, and neither telling the recipient that what they hold is a signed
    refusal this tool does not judge.  R-A018-16(c)'s discipline applied to a
    whole arm: name the thing that is actually there.

    A refusal record travelling BESIDE a decision receipt is refused too, for
    the R-A018-18 reason: a signed refusal riding inside a PASS unread is a
    credential the run certified by omission, and `verify.py` refuses the same
    bundle ("a decision OR a refusal, not both").
    """
    presentation = refusal_presentation(sample, receipt_doc)
    if presentation is None:
        return
    beside = (isinstance(receipt_doc, dict)
              and isinstance(receipt_doc.get("receipt"), dict))
    if beside:
        raise VerificationError(
            f"{presentation}, beside a §5.4 decision receipt: this bundle presents a "
            f"§5.5.1 SignedRefusalRecord (refusal record) AND a signed decision at once. "
            f"§5.5.1 says a bundle presents one or the other, and this verifier does not "
            f"certify refusals nor a decision that travels with one unread -- a signed "
            f"refusal inside a PASS is a record the run certified by omission (D-087(d), "
            f"R-A018-18). verify.py is the tool that authenticates a refusal record"
        )
    raise VerificationError(
        f"{presentation}: this bundle presents a §5.5.1 SignedRefusalRecord (refusal "
        f"record), not a §5.4 decision receipt. This verifier certifies executability and "
        f"does not certify refusals: a refusal is executable at neither Vault entry point, "
        f"and its digest, signature and bindings are not examined here (D-087(d): "
        f"recognised and refused, not verified). verify.py is the tool that authenticates "
        f"a refusal record"
    )


def check_verdict(receipt, execution_path):
    """R-A018-01.  Agree with the Vault about which receipts are executable.

    The predicate used never to read `receipt["verdict"]` at all: the word did not
    occur in this file.  A BLOCK receipt -- including the corpus's real prompt
    injection case -- printed PASS and exited 0.
    """
    raw = receipt.get("verdict")
    try:
        verdict = eip712.parse_uint("uint8", raw)
    except (eip712.EncodingError, ValueError) as exc:
        raise VerificationError(
            f"receipt.verdict {raw!r} is not a canonical uint8: {exc}"
        ) from exc
    if verdict not in VERDICT_NAMES:
        raise VerificationError(
            f"receipt.verdict {raw!r} is outside SentinelTypes.Verdict "
            f"{{0=BLOCK, 1=REVIEW, 2=ALLOW}}. A verdict this verifier cannot name fails "
            f"closed; it is not fallen through to an ALLOW comparison"
        )
    name = VERDICT_NAMES[verdict]

    if execution_path == AUTOMATIC_PATH:
        if verdict == ALLOW:
            return name
        if verdict == REVIEW:
            detail = (
                "A REVIEW receipt is the Vault's owner-override path: it is executable only "
                "through executeWithOverride, on a separate owner-signed override naming this "
                "exact receipt, action and nonce. Nothing here presents one, and a REVIEW "
                "bundle must not pass as though it were an ALLOW. Re-run with "
                "--execution-path owner-override to have that override authenticated."
            )
        else:
            detail = (
                "There is no execution path for a BLOCK receipt: executeWithReceipt reverts "
                "NotAllowVerdict and executeWithOverride reverts NotReviewVerdict."
            )
        raise VerificationError(
            f"receipt.verdict is {name} ({verdict}), not ALLOW: the Vault's automatic path "
            f"executeWithReceipt reverts NotAllowVerdict on this receipt. {detail}"
        )

    if execution_path == OVERRIDE_PATH:
        if verdict == REVIEW:
            return name
        raise VerificationError(
            f"receipt.verdict is {name} ({verdict}), not REVIEW: the Vault's override path "
            f"executeWithOverride reverts NotReviewVerdict, so no owner override can make "
            f"this receipt executable"
        )

    raise VerificationError(
        f"unknown execution path {execution_path!r}; expected {AUTOMATIC_PATH!r} or "
        f"{OVERRIDE_PATH!r}"
    )


def check_owner_override(sample, receipt, action, domain, manifest, now, verdict_name):
    """Examine a §5.5 credential, modelled on `SentinelVault.executeWithOverride`.

    Every binding that function requires is required here: the override must name
    this exact review receipt, this exact action, this exact mandate, policy and
    nonce; its window must be non-empty and current; and it must recover to the
    manifest's owner rather than to the Sentinel signer, because an override the
    signer could mint would not be an independent human authorization at all
    (§3.3(7)).

    R-A018-20.  Every refusal below names the artifact it is about.  It did not:
    a payload missing a binding was indexed straight into a bare `KeyError`, so
    the CLI printed `FAIL: 'reviewReceiptHash'` -- no file, no artifact, no
    §5.5 -- and a payload with a missing or surplus field reached the hasher
    from inside the signature try/except and was announced as *"owner override
    signature verification failed"*, which is R-A018-16(c)'s field-error-as-
    signature-error in this arm.  The sibling artifact `mandate-signature.json`
    had an explicit shape check and this one had none.

    R-A018-18, ruled at D-083(c).  THIS FUNCTION IS NO LONGER THE OVERRIDE PATH'S
    PRIVATE BUSINESS: `verify()` calls it whenever a bundle carries an
    `override.json`, on either path.  Before that it ran only when the caller typed
    `--execution-path owner-override`, so an ALLOW bundle could carry a genuine,
    correctly-bound, outsider-signed §5.5 authorization and certify with the file
    never opened -- a signed credential riding inside a PASS, unexamined.
    `verify.py::_override_checks` has been in its UNCONDITIONAL check list since
    D-023 and refuses exactly that bundle.  The discipline was lost when `a38cff9`
    rebuilt this surface fresh instead of deriving it from the reviewed one, which
    makes this D-052(b)/A-059 reintroduced -- a finding this project made once,
    fixed once, and lost.
    """
    # THE PAIRING, BEFORE THE CREDENTIAL. §5.5: an override targets a REVIEW
    # receipt, and `executeWithOverride` reverts `NotReviewVerdict` on anything
    # else -- so against an ALLOW or a BLOCK receipt there is no such thing as a
    # good override, and nothing about the credential itself can change that.
    #
    # It is checked FIRST, where `_override_checks` checks it last, because that
    # function accumulates every check and reports them together while this module
    # refuses at the first failure. Authenticating first would answer an ALLOW
    # bundle carrying an outsider's credential with "override ownerAddress ... !=
    # ..." -- true, and the wrong thing to send a recipient to fix, because
    # correcting the owner would not make the bundle certifiable either. That is
    # R-A018-16(c)'s discipline -- do not report as at fault the one thing that was
    # fine -- applied to a pairing rather than to a field. On the override path
    # `check_verdict` has already established REVIEW, so this can only fire on a
    # path that could not have used the credential anyway.
    if verdict_name != "REVIEW":
        raise VerificationError(
            f"override.json is present, but the receipt it authorises is {verdict_name}, "
            f"not REVIEW: §5.5 says an override targets a review receipt, and the Vault "
            f"agrees at both entry points -- executeWithReceipt takes no override "
            f"parameter and executeWithOverride reverts NotReviewVerdict. This credential "
            f"is executable nowhere, and it is examined on every path rather than only on "
            f"the one that could use it, because a §5.5 authorization a run never opens is "
            f"one that run certifies unread (R-A018-18)"
        )

    doc = read_json(required(sample, "override.json"))
    override = doc.get("override") if isinstance(doc, dict) else None
    signature = doc.get("ownerSignature") if isinstance(doc, dict) else None
    if not isinstance(override, dict) or not isinstance(signature, str):
        raise VerificationError(
            "override.json must carry an `override` payload and an `ownerSignature`"
        )

    # THE SHAPE, BEFORE ANY FIELD IS INDEXED. §5.5's OverrideAuthorizationPayload
    # is a closed nine-field struct; `eip712.OVERRIDE_FIELDS` is the single source
    # of truth for it, so this check cannot drift from what is actually hashed.
    names = [name for _, name in eip712.OVERRIDE_FIELDS]
    missing = [name for name in names if name not in override]
    surplus = sorted(key for key in override if key not in set(names))
    if missing or surplus:
        faults = []
        if missing:
            faults.append(f"it is missing {missing}")
        if surplus:
            faults.append(f"it carries {surplus}, which §5.5 does not define")
        raise VerificationError(
            f"the `override` payload in override.json is not a §5.5 "
            f"OverrideAuthorizationPayload: " + " and ".join(faults) + f". The struct "
            f"is a closed set of nine fields ({', '.join(names)}); a payload that is "
            f"not exactly those is not the credential the owner signed, and it is "
            f"refused here rather than hashed for the part of it that is recognised"
        )

    if "ownerAddress" in doc:
        eq("override ownerAddress", doc["ownerAddress"], manifest["owner"])

    eq("override.reviewReceiptHash", override["reviewReceiptHash"],
       hx(eip712.receipt_struct_hash(receipt)))
    eq("override.actionHash", override["actionHash"], receipt["actionHash"])
    eq("override.mandateHash", override["mandateHash"], action["mandateHash"])
    eq("override.policyHash", override["policyHash"], action["policyHash"])
    eq("override.actionNonce", override["actionNonce"], action["actionNonce"])

    # NAMED, like `check_verdict`'s. The receipt, mandate, policy and action all
    # carry uint64 time fields too, so the encoder's unattributed "uint64 value
    # '0123' is not a canonical decimal string" left a recipient with four other
    # artifacts to re-check before finding the one at fault.
    window = {}
    for field in ("issuedAt", "expiresAt"):
        raw = override[field]
        try:
            window[field] = eip712.parse_uint("uint64", raw)
        except (eip712.EncodingError, ValueError) as exc:
            raise VerificationError(
                f"override.{field} {raw!r} in override.json is not a canonical "
                f"uint64: {exc}"
            ) from exc
    issued_at = window["issuedAt"]
    expires_at = window["expiresAt"]
    if issued_at >= expires_at:
        raise VerificationError(
            f"owner override has an empty validity window: issuedAt {issued_at} >= "
            f"expiresAt {expires_at}"
        )
    if not issued_at <= now < expires_at:
        raise VerificationError(
            f"owner override requires issuedAt <= evaluationTime < expiresAt; got "
            f"{issued_at} <= {now} < {expires_at}"
        )

    check_signature_form("owner override signature", signature)
    try:
        recovered = recover_address(eip712.override_digest(domain, override), signature)
    except (RecoveryError, eip712.EncodingError, ValueError) as exc:
        raise VerificationError(f"owner override signature verification failed: {exc}") from exc
    eq("recovered owner override signer", recovered, manifest["owner"])
    if recovered == str(manifest["signer"]).lower():
        raise VerificationError(
            "the owner override recovers to the Sentinel signer, so the signer could mint "
            "its own override; §3.3(7) requires the override to be a credential the "
            "isolated signer cannot produce"
        )
    return hx(eip712.override_hash(override))


def check_exact_action(mandate, policy, action, calldata, now):
    """R-A018-05.  The checks the "exact action" banner was already claiming.

    Target, value against both ceilings, selector, operation and policy validity.
    None of them existed: a bundle could be internally perfect -- correct hashes,
    valid owner signature, valid signer signature -- and send an entirely
    different call to an entirely different contract, and this verifier printed
    "exact action".

    NOT covered here, and named so a green run is not read as more than it is:
    the calldata's *arguments* are never decoded, so the mandated beneficiary
    inside `callData` is not compared to `mandate.beneficiary` by any decoding of
    this tool's own.  That is R-A018-17, and it is SETTLED rather than pending --
    D-083(b) ruled the binding disclosed-only, so this function will not grow a
    decoder and the frozen contract's
    `test_calldata_redirecting_the_mandated_beneficiary_is_refused` is
    permanently red by ruling.  What D-087(b) added instead lives in
    `check_attested_record_conforms_to_mandate`: the signer's ATTESTED decoded
    record is compared to the mandate, which catches an honest-but-misconfigured
    evaluator and not a lying one; NOT_ESTABLISHED is where a recipient is told.
    `mandate.targetCodeHash` is likewise not checked, because that needs the live
    chain (R-A018-04).
    """
    if str(action["target"]).lower() != str(mandate["target"]).lower():
        raise VerificationError(
            f"action.target {action['target']!r} is not the mandated target "
            f"{mandate['target']!r}: the owner authorized a call to one contract and this "
            f"bundle carries a call to another"
        )

    value = eip712.parse_uint("uint256", action["valueWei"])
    mandate_ceiling = eip712.parse_uint("uint256", mandate["maxNativeValueWei"])
    if value > mandate_ceiling:
        raise VerificationError(
            f"action.valueWei {value} exceeds the mandate ceiling "
            f"maxNativeValueWei {mandate_ceiling}"
        )
    policy_ceiling = eip712.parse_uint("uint256", policy["maxNativeValueWei"])
    if value > policy_ceiling:
        raise VerificationError(
            f"action.valueWei {value} exceeds the policy ceiling "
            f"policy.maxNativeValueWei {policy_ceiling}"
        )

    # Compared as BYTES, not as strings: `hex_to_bytes` refuses whitespace and odd
    # lengths rather than stripping them, so "0xc1 88528b" cannot spell its way
    # past a string comparison the way `bytes.fromhex` would allow.
    mandated_selector = eip712.hex_to_bytes(mandate["selector"], "mandate.selector")
    if len(mandated_selector) != 4:
        raise VerificationError(
            f"mandate.selector {mandate['selector']!r} is not a 4-byte selector"
        )
    call_bytes = eip712.hex_to_bytes(calldata, "action.callData")
    if len(call_bytes) < 4:
        raise VerificationError(
            f"action.callData {calldata!r} is shorter than a 4-byte selector, so it cannot "
            f"carry the mandated selector 0x{mandated_selector.hex()}"
        )
    if call_bytes[:4] != mandated_selector:
        raise VerificationError(
            f"action.callData carries selector 0x{call_bytes[:4].hex()}, not the mandated "
            f"selector 0x{mandated_selector.hex()}"
        )

    # THE VAULT'S RULE FIRST, UNCONDITIONALLY (D-087(a); SentinelVault.sol:357).
    # `if (action.operation != uint8(T.Operation.CALL)) revert UnsupportedOperation();`
    # is not conditioned on the policy: DELEGATECALL (1) and CREATE (2) are
    # commented "unsupported, never executes", and there is no policy field that
    # can enable them. The comparison to `policy.allowedOperation` below used to
    # be the ONLY check, so a policy saying 1 and an action saying 1 agreed with
    # each other, certified here, and reverted on chain -- the A-and-B-versus-C
    # axis no round had named. Refused here BEFORE the policy comparison, and
    # without blaming the policy, because when the policy agreed with the action
    # the policy was the one thing that was fine (R-A018-16(c)).
    operation = eip712.parse_uint("uint8", action["operation"])
    if operation != CALL_OPERATION:
        raise VerificationError(
            f"action.operation is {operation}, not CALL ({CALL_OPERATION}): SentinelVault "
            f"reverts UnsupportedOperation on any operation other than CALL, "
            f"unconditionally -- SentinelTypes.Operation numbers DELEGATECALL 1 and CREATE "
            f"2 and neither ever executes, and no policy field can enable them. This is "
            f"refused regardless of what policy.allowedOperation says"
        )
    allowed_operation = eip712.parse_uint("uint8", policy["allowedOperation"])
    if operation != allowed_operation:
        raise VerificationError(
            f"action.operation {operation} is not the policy's allowedOperation "
            f"{allowed_operation}: a different execution mode has a different blast radius"
        )

    policy_after = eip712.parse_uint("uint64", policy["validAfter"])
    policy_until = eip712.parse_uint("uint64", policy["validUntil"])
    if not policy_after <= now < policy_until:
        raise VerificationError(
            f"policy is not current at evaluationTime {now}; its window is "
            f"[{policy_after}, {policy_until})"
        )


def check_evidence_describes_the_bundle(evidence, action, mandate, policy, receipt,
                                        verdict_name):
    """§5.6.  The evidence bundle must DESCRIBE the documents it is signed over.

    Ported from `verify.py::_evidence_describes_the_bundle` and the anchor /
    verdict tail of `_chain_checks` (D-087(a), inventory diff O2 -- the
    severity-1 cell).  Before this function existed, `receipt.evidenceHash` made
    `evidence.json` tamper-EVIDENT and nothing made it TRUE: the artifact a
    recipient actually reads could be replaced wholesale with `{"note": ...}`,
    re-canonicalised, re-hashed, re-signed, and certify.  The run authenticated
    that the evidence was THE bundle the signer signed over and never that it
    described THIS action.

    This does not make the verifier a second evaluator.  `normalizedAction` is
    the §5.3 ActionPayload restated verbatim plus `callData`; `expectedEffects`
    is six mandate fields, one policy field and the intersected native ceiling;
    `anchor` is the receipt's simulation block; `verdict` is the receipt's enum
    spelled out.  All four are pure projections, and the only question asked is
    "does this bundle describe the documents it claims to describe".

    ABSENCE IS NOT AGREEMENT (A-067, D-052(b)).  A bundle that does not carry a
    required projection is refused, because omission is the cheapest evasion
    and must cost more than a contradiction, not less.  What IS tolerated, as
    `verify.py` tolerates it: an individual field absent from a present
    `expectedEffects`, and a present `normalizedAction` without `callData` --
    the bytes are bound by `dataHash` either way.

    Every refusal names `evidence.json` and the projection at fault, so it is
    never mistaken for a hash or signature failure (R-A018-16(c)).
    """
    if not isinstance(evidence, dict):
        raise VerificationError(
            f"evidence.json is a JSON {type(evidence).__name__}, not an object, so it "
            f"carries none of the §5.6 projections (normalizedAction, expectedEffects, "
            f"anchor, verdict) and describes nothing; it canonicalises and hashes "
            f"perfectly well, which is why the hash chain did not refuse it"
        )

    def shape(name, value):
        return ("absent from evidence.json" if value is None
                else f"a JSON {type(value).__name__} in evidence.json, not an object")

    normalized = evidence.get("normalizedAction")
    if not isinstance(normalized, dict):
        raise VerificationError(
            f"evidence.normalizedAction is {shape('normalizedAction', normalized)}: §5.6 "
            f"requires the action restated inside the evidence, and a bundle that omits "
            f"the projection is not certified as describing the action it claims to "
            f"(absence is not agreement)"
        )
    mismatched = []
    for _type, name in eip712.ACTION_FIELDS:
        if name not in normalized:
            mismatched.append(f"{name} is absent from normalizedAction")
        elif not same(normalized[name], action.get(name)):
            mismatched.append(
                f"{name}: evidence {normalized[name]!r} vs action {action.get(name)!r}")
    if mismatched:
        raise VerificationError(
            "evidence.normalizedAction in evidence.json does not restate the §5.3 action "
            "in action.json -- the dashboard describes a call this bundle does not carry: "
            + "; ".join(mismatched)
        )
    declared = normalized.get("callData")
    if declared is not None:
        try:
            digest = hx(keccak256(eip712.hex_to_bytes(
                declared, "evidence.normalizedAction.callData")))
        except (eip712.EncodingError, ValueError) as exc:
            raise VerificationError(
                f"evidence.normalizedAction.callData in evidence.json is not hex the "
                f"dataHash could have been computed over: {exc}"
            ) from exc
        if digest != str(action.get("dataHash")).lower():
            raise VerificationError(
                f"keccak256(evidence.normalizedAction.callData) {digest} != action.dataHash "
                f"{action.get('dataHash')}: the evidence agrees with the action field by "
                f"field, but the bytes it says it was computed over are not the bytes the "
                f"action binds"
            )

    if "verdict" not in evidence:
        raise VerificationError(
            "evidence.verdict is absent from evidence.json (§5.6): a bundle that omits its "
            "own verdict cannot be compared against the signed receipt's, and absence is "
            "not agreement"
        )
    if evidence["verdict"] != verdict_name:
        raise VerificationError(
            f"evidence.verdict {evidence['verdict']!r} in evidence.json disagrees with the "
            f"signed receipt's verdict {verdict_name}: the dashboard and the receipt tell "
            f"a recipient different stories, and only the receipt is signed"
        )

    anchor = evidence.get("anchor")
    if not isinstance(anchor, dict):
        raise VerificationError(
            f"evidence.anchor is {shape('anchor', anchor)} (§5.6): the anchor is what a "
            f"reader is shown as the simulation's block, and deleting it is the cheaper "
            f"attack on the same binding as rewriting it"
        )
    if (str(anchor.get("blockNumber")) != str(receipt.get("simulationBlockNumber"))
            or not same(anchor.get("blockHash"), receipt.get("simulationBlockHash"))):
        raise VerificationError(
            f"evidence.anchor {anchor} in evidence.json does not match the signed "
            f"receipt's simulation block {receipt.get('simulationBlockNumber')} "
            f"{receipt.get('simulationBlockHash')}"
        )

    expected = evidence.get("expectedEffects")
    if not isinstance(expected, dict):
        raise VerificationError(
            f"evidence.expectedEffects is {shape('expectedEffects', expected)} (§5.6): "
            f"the projection of the signed mandate and policy a recipient reads is "
            f"missing, and absence is not agreement"
        )
    wrong = []
    for name in EXPECTED_EFFECTS_FROM_MANDATE:
        if name in expected and not same(expected[name], mandate.get(name)):
            wrong.append(f"{name}: evidence {expected[name]!r} vs mandate {mandate.get(name)!r}")
    if "maxAllowanceIncreaseBaseUnits" in expected and not same(
            expected["maxAllowanceIncreaseBaseUnits"],
            policy.get("maxAllowanceIncreaseBaseUnits")):
        wrong.append(
            f"maxAllowanceIncreaseBaseUnits: evidence "
            f"{expected['maxAllowanceIncreaseBaseUnits']!r} vs policy "
            f"{policy.get('maxAllowanceIncreaseBaseUnits')!r}")
    # §5.2, published: "Mandate and policy constraints are intersected." The
    # binding native ceiling is the LOWER of the two, not the mandate's; compared
    # against the mandate alone this would be wrong the first time they diverge.
    if "maxNativeValueWei" in expected:
        bound = min(eip712.parse_uint("uint256", mandate["maxNativeValueWei"]),
                    eip712.parse_uint("uint256", policy["maxNativeValueWei"]))
        try:
            projected = eip712.parse_uint("uint256", expected["maxNativeValueWei"])
        except (eip712.EncodingError, ValueError, TypeError):
            projected = None
        if projected != bound:
            wrong.append(
                f"maxNativeValueWei: evidence {expected['maxNativeValueWei']!r} vs the §5.2 "
                f"intersection {bound} of the mandate's and the policy's ceilings")
    if wrong:
        raise VerificationError(
            "evidence.expectedEffects in evidence.json does not project the signed mandate "
            "and policy: " + "; ".join(wrong)
        )


def check_attested_record_conforms_to_mandate(evidence, mandate, policy):
    """§5.7.1, from the verifier's side: "signer-attested record conforms to mandate".

    Ported from `verify.py::_allow_conforms_to_the_mandate` under D-087(b), and
    NAMED BY RULING.  The record compared is the signer's own
    `decodedSelectorAndParameters` -- what the isolated signer's evaluator says
    it decoded -- and it is compared against the mandate's purpose fields
    (`resourceId`, `beneficiary`, `durationSeconds`, `recurringAllowed`, the
    approve arm's `spender` and the policy's allowance ceiling) WITHOUT decoding
    `callData`.  D-083(b) ruled this tool decodes nothing and D-087(b) does not
    reverse it.

    WHAT IT CATCHES, AND WHAT IT DOES NOT.  A misconfigured-but-honest evaluator
    that reported a beneficiary the mandate does not name and said ALLOW anyway
    is caught here.  A signer that LIES about what it decoded is not: the record
    it reads is the signer's.  The check is therefore never called "beneficiary
    verified", and the certifying output says in words that it does not catch a
    lying signer -- the standing pattern D-087 records, carry the honest
    version and never let the name claim more than the check establishes.

    BOUND TO ALLOW ONLY, by the caller.  A BLOCK or REVIEW bundle is
    legitimately nonconforming -- that is what it is FOR; the corpus is full of
    them and `case-3-wrong-purpose-block` is the flagship -- and a REVIEW
    receipt executed by an authenticated owner override is the owner's decision
    to proceed.  The verdict is established BEFORE this runs, so a BLOCK bundle
    is refused for its verdict and never for its conformance (R-A018-16(c): the
    recipient is told the signer said BLOCK, not that a resourceId disagrees).

    ABSENCE IS NOT AGREEMENT.  Under ALLOW, a missing or non-object record, a
    record without parameters, a record attesting the call was NOT decoded, or
    a schema this verifier cannot evaluate all refuse: an ALLOW nobody can
    check is not an ALLOW anybody should certify.
    """
    prefix = CONFORMANCE_CHECK_NAME + " (§5.7.1, compared from the signer's own attested " \
             "decodedSelectorAndParameters in evidence.json, without decoding callData)"
    dsp = evidence.get("decodedSelectorAndParameters")
    if not isinstance(dsp, dict):
        raise VerificationError(
            f"{prefix}: the ALLOW carries no decodedSelectorAndParameters record to compare "
            f"({'absent' if dsp is None else 'got a JSON ' + type(dsp).__name__}); absence "
            f"is not agreement, and an ALLOW nobody can check is not one to certify"
        )
    params = dsp.get("parameters")
    if not isinstance(params, dict):
        raise VerificationError(
            f"{prefix}: the attested record carries no parameters object "
            f"({'absent' if params is None else 'got a JSON ' + type(params).__name__}), "
            f"so it attests nothing comparable"
        )
    if str(dsp.get("decoded")).lower() not in ("true", "1"):
        raise VerificationError(
            f"{prefix}: the record attests decoded={dsp.get('decoded')!r}; an undecoded "
            f"call cannot be ALLOWed, and an ALLOW nobody can check is not one to certify"
        )
    if not same(dsp.get("selector"), mandate.get("selector")):
        raise VerificationError(
            f"{prefix}: the attested selector {dsp.get('selector')!r} is not the mandated "
            f"selector {mandate.get('selector')!r}; the signer attests to having decoded a "
            f"different function than the mandate authorises"
        )

    schema, wrong = dsp.get("schema"), []
    if schema == "DemoPay.purchase":
        for name in ("resourceId", "beneficiary"):
            if not same(params.get(name), mandate.get(name)):
                wrong.append(f"{name}: attested {params.get(name)!r} vs mandate "
                             f"{mandate.get(name)!r}")
        try:
            if int(params.get("durationSeconds")) != int(mandate.get("durationSeconds")):
                wrong.append(f"durationSeconds: attested {params.get('durationSeconds')!r} "
                             f"vs mandate {mandate.get('durationSeconds')!r}")
        except (TypeError, ValueError) as exc:
            wrong.append(f"durationSeconds: unreadable ({exc})")
        if params.get("recurring") and not mandate.get("recurringAllowed"):
            wrong.append("recurring: the attested record requests recurrence and "
                         "mandate.recurringAllowed forbids it")
    elif schema == "DemoERC20.approve":
        if not same(params.get("spender"), mandate.get("beneficiary")):
            wrong.append(f"spender: attested {params.get('spender')!r} is not the mandate's "
                         f"beneficiary {mandate.get('beneficiary')!r}")
        ceiling = policy.get("maxAllowanceIncreaseBaseUnits")
        try:
            if ceiling is None:
                wrong.append("amount: the policy carries no maxAllowanceIncreaseBaseUnits "
                             "ceiling to compare the approval against")
            elif int(params.get("amount")) > int(ceiling):
                wrong.append(f"amount: attested {params.get('amount')!r} exceeds the "
                             f"policy's allowance ceiling maxAllowanceIncreaseBaseUnits "
                             f"{ceiling!r}")
        except (TypeError, ValueError) as exc:
            wrong.append(f"amount: unreadable ({exc})")
    else:
        wrong.append(f"schema {schema!r} is not one this verifier can check conformance "
                     f"for, and an ALLOW it cannot check is an ALLOW it cannot certify")

    if wrong:
        raise VerificationError(f"{prefix}: " + "; ".join(wrong))


def check_reason_codes(receipt_doc, receipt):
    """§5.4 as amended by D-022.  The published list must be the committed one.

    Ported from `verify.py::_reason_code_checks` (D-087(a), inventory diff O4).
    `receipt.reasonCodesHash` is signed; the `reasonCodes` array beside the
    receipt is what a recipient is shown, and until this function existed the
    two were never compared, so the codes shown could be swapped freely.  It
    bites hardest on the override path, where an owner deciding whether to
    override reads the explanation.

    THE HASH IS §5.4's OWN CONSTRUCTION, via `reasoncodes.py`: de-duplicated,
    sorted in ascending byte order, joined with U+000A, keccak256 -- and the
    identifier grammar is applied with absolute anchors BEFORE anything is
    hashed.  A naive join would let `{"EVIL\\nINJECTED"}` commit, byte for byte,
    to the same preimage as `{"EVIL", "INJECTED"}`; only the grammar refuses it.
    The grammar check is therefore a refusal in its own right and runs first,
    so a bad identifier is reported as a bad identifier and never as a hash
    mismatch (R-A018-16(c)).

    `signerFindings` must be inside the committed set: §5.4 defines that set as
    the UNION of the evaluator's codes and the signer's findings, so a finding
    outside `reasonCodes` means the receipt commits to the evaluator's half
    only.  An absent `signerFindings` array is tolerated, as `verify.py`
    tolerates it; an absent `reasonCodes` array is not.  Order and duplicates
    in the published list are NOT refused: the hash is order- and
    duplicate-insensitive by construction, and `verify.py` carries that as an
    advisory that cannot fail.
    """
    published = receipt_doc.get("reasonCodes")
    findings = receipt_doc.get("signerFindings")
    if published is None:
        raise VerificationError(
            "receipt.json carries no reasonCodes array: §5.4 requires the full list to "
            "travel alongside the receipt and a verifier must be given it. Without it the "
            "signed reasonCodesHash commitment cannot be checked, and not being given the "
            "list is a refusal for a signed receipt, not a clean slate"
        )
    if not isinstance(published, list):
        raise VerificationError(
            f"reasonCodes in receipt.json is a JSON {type(published).__name__}, not the "
            f"list §5.4 defines"
        )
    if findings is not None and not isinstance(findings, list):
        raise VerificationError(
            f"signerFindings in receipt.json is a JSON {type(findings).__name__}, not a list"
        )
    try:
        reasoncodes.validate_all(published)
        if findings is not None:
            reasoncodes.validate_all(findings)
    except reasoncodes.ReasonCodeError as exc:
        raise VerificationError(
            f"a reason-code identifier in receipt.json fails the §5.4 grammar "
            f"^[A-Za-z0-9_.:-]{{1,64}}$ (matched with absolute anchors), so the "
            f"commitment is not recomputed over it: {exc}"
        ) from exc

    computed = reasoncodes.reason_codes_hash_hex(published)
    declared = str(receipt.get("reasonCodesHash")).lower()
    if computed != declared:
        committed = reasoncodes.committed_set(published)
        raise VerificationError(
            f"receipt.reasonCodesHash {declared} is not the §5.4 hash of the published "
            f"reasonCodes list in receipt.json ({computed} over the de-duplicated, "
            f"byte-sorted, newline-joined set of {len(committed)} code(s)): the reason "
            f"codes a recipient is shown are not the ones the signer committed to"
        )
    if findings is not None:
        missing = sorted(set(findings) - set(published))
        if missing:
            raise VerificationError(
                f"signerFindings {missing} in receipt.json are absent from the committed "
                f"reason-code set: §5.4 defines that set as the union of the evaluator's "
                f"codes and the signer's findings, so this receipt commits to the "
                f"evaluator's half only"
            )


def verify(sample, manifest_path, authority, evaluation_time=None,
           execution_path=AUTOMATIC_PATH):
    sample = os.path.abspath(sample)

    # THE CLOCK, FIRST, BECAUSE THE MANIFEST'S OWN LIFETIME IS JUDGED AT IT.
    #
    # R-A018-03. "Non-overridable clock" is underspecified -- the host's system
    # clock is caller-controlled too -- so neither branch below claims a trusted
    # time source. What separates them is WHOSE choice it is. Without the flag the
    # instant comes from the machine running the check, which is the recipient's.
    # With the flag it comes from whoever composed the command line, which is
    # exactly the presenter's position, so that run is a diagnostic and certifies
    # nothing.
    #
    # D-086(e): the instant is pinned ONCE, here, and every window below -- the
    # manifest's lifetime included -- is judged at this one value. There is no
    # path on which `deployment.verify` is reached without it; `deployment.py`
    # now refuses such a call rather than skipping the bound.
    if evaluation_time is None:
        now = int(time.time())
        time_source = (
            "the host clock of the machine running this check; NOT an authenticated block "
            "timestamp, so executability at a block is not established (R-A018-03)"
        )
        mode = MODE_STATIC
    else:
        now = int(evaluation_time)
        time_source = (
            "--evaluation-time, chosen by whoever invoked this tool. Non-certifying test "
            "mode: findings below are diagnostics and certify nothing (R-A018-03)"
        )
        mode = MODE_DIAGNOSTIC

    manifest = deployment.verify(read_json(manifest_path), authority, evaluation_time=now)

    # THE SHAPE OF WHAT WAS PRESENTED, BEFORE ANY ARTIFACT IS REQUIRED (D-087(d)).
    # A §5.5.1 refusal bundle carries a receipt.json with no `receipt` member, or
    # a refusal.json and no receipt.json at all. `required()` would name the
    # wrong artifact for both; this names the one that is there.
    receipt_path = os.path.join(sample, "receipt.json")
    receipt_doc = read_json(receipt_path) if os.path.isfile(receipt_path) else None
    check_not_a_refusal_record(sample, receipt_doc)

    mandate = read_json(required(sample, "mandate.json"))
    policy = read_json(required(sample, "policy.json"))
    action = read_json(required(sample, "action.json"))
    required(sample, "receipt.json")
    mandate_sig = read_json(required(sample, "mandate-signature.json"))
    evidence_raw = read_bytes(required(sample, "evidence.json"))
    canonical_file = read_bytes(required(sample, "evidence.canonical.json"))
    evidence_hash_file = read_bytes(required(sample, "evidence.hash")).decode().strip().lower()
    receipt = receipt_doc.get("receipt") if isinstance(receipt_doc, dict) else None
    receipt_signature = receipt_doc.get("signature") if isinstance(receipt_doc, dict) else None
    if not isinstance(receipt, dict) or not isinstance(receipt_signature, str):
        raise VerificationError("receipt.json must carry a signed decision receipt")

    domain = {
        "name": "Sentinel",
        "version": "0.3",
        "chainId": manifest["chainId"],
        "verifyingContract": manifest["vault"],
    }

    evidence = jcs.parse_bytes(evidence_raw)
    canonical = jcs.canonicalize(evidence)
    if canonical != canonical_file:
        raise VerificationError("evidence canonicalization mismatch")
    evidence_hash = hx(keccak256(canonical))
    eq("evidence.hash", evidence_hash_file, evidence_hash)

    mandate_hash = hx(eip712.mandate_hash(mandate))
    policy_hash = hx(eip712.policy_hash(policy))
    action_hash = hx(eip712.action_hash(action))
    eq("action.mandateHash", action["mandateHash"], mandate_hash)
    eq("action.policyHash", action["policyHash"], policy_hash)
    eq("receipt.actionHash", receipt["actionHash"], action_hash)
    eq("receipt.mandateHash", receipt["mandateHash"], mandate_hash)
    eq("receipt.policyHash", receipt["policyHash"], policy_hash)
    eq("receipt.evidenceHash", receipt["evidenceHash"], evidence_hash)

    for label, doc in (("mandate", mandate), ("policy", policy), ("action", action)):
        eq(f"{label}.chainId", doc["chainId"], manifest["chainId"])
        eq(f"{label}.vault", doc["vault"], manifest["vault"])
    eq("mandate.principal", mandate["principal"], manifest["owner"])
    eq("mandate.signer", mandate["signer"], manifest["signer"])
    eq("receipt.signer", receipt["signer"], manifest["signer"])
    eq("mandate.policyHash", mandate["policyHash"], policy_hash)

    calldata = action.get("callData")
    if not isinstance(calldata, str):
        raise VerificationError("action.callData is required for exact-call verification")
    eq("action.dataHash", action["dataHash"], hx(keccak256(eip712.hex_to_bytes(calldata))))

    if set(mandate_sig) != {"ownerAddress", "ownerSignature"}:
        raise VerificationError("mandate-signature.json has an unexpected shape")
    eq("mandate signature owner", mandate_sig["ownerAddress"], manifest["owner"])
    check_signature_form("mandate owner signature", mandate_sig["ownerSignature"])
    check_signature_form("receipt signer signature", receipt_signature)
    try:
        mandate_owner = recover_address(
            eip712.mandate_digest(domain, mandate), mandate_sig["ownerSignature"]
        )
        receipt_signer = recover_address(
            eip712.receipt_digest(domain, receipt), receipt_signature
        )
    except (RecoveryError, eip712.EncodingError, ValueError) as exc:
        raise VerificationError(f"signature verification failed: {exc}") from exc
    eq("recovered mandate owner", mandate_owner, manifest["owner"])
    eq("recovered receipt signer", receipt_signer, manifest["signer"])

    # THE VERDICT, BEFORE THE ACTION PREDICATE AND BEFORE THE CONTENT ARMS.
    # Deliberate ordering: the corpus's BLOCK bundles are blocked precisely
    # BECAUSE their action does not match the mandate, and a recipient handed
    # `case-2-injection-block` should be told the signer said BLOCK, not merely
    # that a target field disagrees -- nor, since D-087(b), that the signer's
    # attested beneficiary disagrees, which is exactly WHY the cold demo's BLOCK
    # receipt is BLOCK. The verdict is the gate; everything after it is about a
    # receipt the Vault could execute.
    verdict_name = check_verdict(receipt, execution_path)

    check_exact_action(mandate, policy, action, calldata, now)

    valid_after = eip712.parse_uint("uint64", mandate["validAfter"])
    valid_until = eip712.parse_uint("uint64", mandate["validUntil"])
    issued_at = eip712.parse_uint("uint64", receipt["issuedAt"])
    expires_at = eip712.parse_uint("uint64", receipt["expiresAt"])
    deadline = eip712.parse_uint("uint64", action["deadline"])
    if not valid_after <= now < valid_until:
        raise VerificationError(f"mandate is not current at evaluationTime {now}")
    if not issued_at <= now < expires_at:
        raise VerificationError(
            f"receipt requires issuedAt <= evaluationTime < expiresAt; got {issued_at} <= {now} < {expires_at}"
        )
    if now > deadline:
        raise VerificationError("action deadline has passed")

    # R-A018-02. What stood here was a comparison of the parsed uint256 nonce
    # against zero, which `parse_uint` makes unreachable: it returns a
    # non-negative int or raises, so the branch body could never run. It read as
    # a freshness check and was not one. What remains is a well-formedness
    # check and nothing more, because nonce freshness is not observable offline --
    # the Vault consumes the nonce atomically at execution. See NOT_ESTABLISHED.
    eip712.parse_uint("uint256", action["actionNonce"])

    # R-A018-18, ruled at D-083(c): THE CREDENTIAL IS EXAMINED ON EVERY PATH.
    # The condition is "the caller declared the override path, OR the bundle carries
    # the file" -- not "the caller declared the override path". The first disjunct
    # keeps the existing refusal for a REVIEW bundle presented on that path with no
    # credential at all (`required` names the missing artifact); the second is the
    # repair, and it is what stops an `override.json` beside an ALLOW receipt from
    # being passed over in silence. Matching `verify.py::_override_checks`, which
    # returns early only when the file is absent.
    override_hash = None
    if execution_path == OVERRIDE_PATH or os.path.isfile(
            os.path.join(sample, "override.json")):
        override_hash = check_owner_override(
            sample, receipt, action, domain, manifest, now, verdict_name)

    # THE CONTENT ARMS (D-087(a)/(b)), after the executability predicate has been
    # established for this receipt on this path. Their order among themselves:
    # the §5.6 projections first, because they establish that evidence.json
    # describes THESE documents at all; the §5.7.1 conformance of the signer's
    # attested record next, under ALLOW only; the §5.4 reason-code commitment
    # last. A bundle refused here is an authentic, executable-looking bundle whose
    # evidence does not describe it, and the refusal says which projection.
    check_evidence_describes_the_bundle(evidence, action, mandate, policy, receipt,
                                        verdict_name)
    if verdict_name == "ALLOW":
        check_attested_record_conforms_to_mandate(evidence, mandate, policy)
    check_reason_codes(receipt_doc, receipt)

    result = {
        "mode": mode,
        "claim": (
            "static, offline executability under the Vault's offline-checkable action "
            "predicate; AUTHENTICITY is verify.py's claim, not this tool's (D-087(c))"
        ),
        "deploymentAuthority": authority.lower(),
        # Authenticated as authority ASSERTIONS, not as facts about a live
        # deployment: nothing here read a chain (R-A018-04). D-086(e) rules that
        # the value is never presented as authenticated, so these travel under a
        # key that says what they are rather than at the top level beside the
        # verdict, where a reader could not tell a verified finding from an
        # unchecked assertion. See NOT_ESTABLISHED, printed alongside.
        "unverifiedAuthorityAssertions": {
            "deploymentBlockNumber": manifest["deploymentBlockNumber"],
            "runtimeCodeHash": manifest["runtimeCodeHash"],
        },
        "mandateHash": mandate_hash,
        "actionHash": action_hash,
        "actionNonce": action["actionNonce"],
        "verdict": verdict_name,
        "executionPath": execution_path,
        "evaluationTime": str(now),
        "evaluationTimeSource": time_source,
        "notEstablished": NOT_ESTABLISHED,
    }
    if override_hash is not None:
        result["ownerOverrideHash"] = override_hash
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("sample", help="publication evidence-bundle directory")
    parser.add_argument("--deployment-manifest", required=True)
    parser.add_argument(
        "--deployment-authority", required=True,
        help="authority address obtained independently of the publication material",
    )
    parser.add_argument(
        "--execution-path", choices=(AUTOMATIC_PATH, OVERRIDE_PATH), default=AUTOMATIC_PATH,
        help="which Vault entry point this bundle is presented for. %(default)s is "
             "executeWithReceipt and requires an ALLOW receipt; owner-override is "
             "executeWithOverride and requires a REVIEW receipt plus an authenticated "
             "owner override in override.json. A BLOCK receipt is executable through "
             "neither (default: %(default)s)",
    )
    parser.add_argument(
        "--evaluation-time", type=int, metavar="UNIX_SECONDS",
        help="NON-CERTIFYING TEST MODE. Evaluate every validity window against this "
             "caller-supplied instant instead of the host clock. Documented rather than "
             "hidden, and deliberately unable to certify: a switch that changes what a "
             "verifier reports must not be invisible to the recipient reading its "
             "interface. A run under this flag prints its findings and exits 3",
    )
    args = parser.parse_args(argv)
    try:
        result = verify(
            args.sample, args.deployment_manifest, args.deployment_authority,
            evaluation_time=args.evaluation_time,
            execution_path=args.execution_path,
        )
    except (OSError, ValueError, KeyError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1

    if result["mode"] != MODE_STATIC:
        print("NOT CERTIFIED: the evaluation instant was supplied by the caller, so every "
              "validity finding below is the caller's frame rather than an observed one. "
              "Diagnostic output only.")
        print(json.dumps(result, sort_keys=True))
        return 3

    # THE HEADLINE IS ONE LINE AND IT CARRIES TWO REPAIRS.
    #
    # R-A018-19 / F5: the override arm used to reprint the automatic arm's
    # sentence verbatim, so "the machine approved this" and "a human was asked
    # and signed" differed by one word -- REVIEW where a reader expected ALLOW --
    # and were otherwise identical outside the JSON. The Vault takes the opposite
    # position at every level: separate entry points, `viaOverride: true`, and
    # under D-043 a dedicated `OverrideAuthorized` event, added precisely because
    # `viaOverride` alone was ruled insufficient for an auditor. A line a
    # recipient reads once should not be the weakest of the three.
    #
    # R-A018-08 / F3: "the action matches the mandate and policy" claimed a
    # semantic conformance nothing here checked. What was compared is target,
    # value, selector and operation, so that is what the sentence now says; the
    # arguments inside callData are named in NOT ESTABLISHED rather than covered
    # by a word like "matches".
    #
    # D-087(a)/(b): the three content arms are enumerated the same way, and the
    # §5.7.1 check is named by its ruled name with what it does not catch said in
    # the same breath. The word "block" is kept out of this line on purpose: the
    # anchor is compared to the RECEIPT's simulation block, not to a chain, and a
    # headline that named a block would anchor a claim to one (D-086(e)).
    compared = ("the action's target, value, selector and operation match the mandate and "
                "policy; the evidence's §5.6 projections (normalizedAction, expectedEffects, "
                "anchor, verdict) describe these documents; the published reason codes are "
                f"the ones the receipt commits to; and the {CONFORMANCE_CHECK_NAME} (§5.7.1, "
                "compared from the signer's own attested record without decoding callData, "
                "so this does not catch a lying signer)")
    if result["executionPath"] == OVERRIDE_PATH:
        print("PASS (static, offline) BY AUTHENTICATED OWNER OVERRIDE, NOT AUTOMATICALLY: the "
              "deployment manifest authenticates under the out-of-band authority; the mandate "
              f"is the owner's; the signer's decision is {result['verdict']}, which the Vault "
              "refuses at executeWithReceipt; a separate owner-signed override naming this "
              "exact receipt, action and nonce was authenticated and recovers to the owner "
              f"rather than the signer; and {compared}.")
    else:
        print("PASS (static, offline): the deployment manifest authenticates under the "
              "out-of-band authority; the mandate is the owner's; the signer's decision is "
              f"{result['verdict']}; and {compared}.")
    # D-087(c): WHICH CLAIM THIS IS, on the surface a recipient reads.
    print("CLAIM: this tool certifies EXECUTABILITY, statically and offline -- that "
          "SentinelVault's offline-checkable action predicate accepts this bundle at the "
          "entry point named above. It is not the authenticity verifier: verify.py "
          "certifies AUTHENTICITY, that the bundle is genuinely what the signer produced, "
          "and reports a BLOCK receipt, a REVIEW receipt with no override, or a §5.5.1 "
          "refusal record -- all of which this tool refuses -- as AUTHENTIC, NOT "
          "EXECUTABLE with exit status 3, not as a PASS (D-090(a), D-091(a)).")
    print("NOT ESTABLISHED by this run: " + "; ".join(NOT_ESTABLISHED) + ".")
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
