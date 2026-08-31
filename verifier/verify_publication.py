#!/usr/bin/env python3
"""Fail-closed verifier for the Sentinel v0.3 publication bundle.

The caller supplies a deployment authority address obtained independently of the
publication material.  That authority signs the deployment manifest, and the
manifest then supplies the chain, vault, owner and signer that every EIP-712
artifact must match.  The presenter has no way to nominate the deployment
identity: `deployment.py` enforces a closed field set, so a manifest naming its
own trust root is refused, and authority reaches this tool only through the
caller's argument.

WHAT A RUN OF THIS TOOL DOES NOT ESTABLISH
------------------------------------------
Recorded here, in the text argparse reprints under --help, because this docstring
previously claimed the opposite of the third item.

* NO CHAIN IS READ.  `runtimeCodeHash`, `deploymentBlockHash` and
  `compilerMetadataHash` are authenticated as things the deployment authority
  SAID.  They are compared against no deployed bytecode and no state proof, so
  this tool cannot tell you the described code is what is deployed, nor that the
  action would execute (R-A018-04).
* NONCE FRESHNESS CANNOT BE ESTABLISHED OFFLINE.  Only the Vault consumes an
  action nonce, atomically, at execution.  An offline verifier can at best
  observe nonce state at an authenticated block, and this one observes none
  (R-A018-02).
* THERE IS NO TRUSTED CLOCK.  Validity windows are evaluated against the host
  clock, which is not an authenticated block timestamp.  `--evaluation-time`
  moves that choice from the machine running the check to whoever writes the
  command line, so a run under that flag reports its findings and then refuses
  to certify anything at all (R-A018-03).
* THE CALLDATA ARGUMENTS ARE NEVER DECODED.  `action.callData` is bound by
  `dataHash` to the bytes presented, and its leading four bytes are compared to
  the mandated selector -- but nothing after that selector is decoded, so a
  beneficiary, recipient or amount encoded inside the calldata is compared to no
  mandated value.  A bundle in which only the beneficiary word was rewritten is
  internally consistent and authenticates here.  Only the isolated signer's
  evaluator decodes those arguments; the Vault, like this tool, binds the bytes.
  RULED DISCLOSED-ONLY, not deferred: D-083(b) settled that this tool decodes
  nothing, and recorded the cost with the ruling -- beneficiary binding rests
  entirely on the isolated signer behaving correctly, with no independent
  downstream check (R-A018-17).

So a successful run is a statement about STATIC AUTHENTICITY, and about
conformance of the fields it actually compares -- target, native value, selector
and operation -- to the signed mandate and policy.  It is not a statement about
executability at a named block, nor about what the calldata's arguments say.

EXECUTION PATHS
---------------
`SentinelVault.sol` has exactly two entry points and deliberately no third.
`executeWithReceipt` reverts `NotAllowVerdict` on anything that is not ALLOW;
`executeWithOverride` reverts `NotReviewVerdict` on anything that is not REVIEW
and additionally requires a separate owner-signed override naming that exact
receipt, action and nonce.  This verifier mirrors that split: the caller declares
which entry point the bundle is presented for with --execution-path, and a BLOCK
receipt is executable through neither.

A BUNDLE'S §5.5 CREDENTIAL IS EXAMINED ON WHICHEVER PATH IT IS PRESENTED FOR, not
only on the one that could use it (R-A018-18, ruled at D-083(c)).  An `override.json`
sitting beside an ALLOW receipt is refused rather than passed over: a credential no
Vault entry point will accept must not ride inside a PASS unopened, because a run
that never reads it certifies it by omission.

EXIT CODES
----------
Listed here, not only in the `--help` text, because a caller wiring this tool
into a script reads the module or the release documentation rather than running
`--help` -- and a third code that only one of those three surfaces mentions is a
code somebody's `if status != 0` will silently mistreat as a refusal.

* **0** -- CERTIFYING.  Static offline authenticity established, with the
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
from keccak import keccak256
from secp256k1 import RecoveryError, is_low_s, parse_signature, recover_address


# -----------------------------------------------------------------------------
# KNOWN RED TESTS IN THE FROZEN CONTRACT, RECORDED SO THEY ARE NOT SILENT
# -----------------------------------------------------------------------------
# `verifier/test_publication_verifier.py` was written by an independent author who
# was forbidden to edit this module (D-058(1), A-028), and it is not editable from
# this side either -- so work this module deliberately does not do cannot be marked
# `expectedFailure` in the suite and has to be declared here instead. FOUR of its 81
# tests are RED ON PURPOSE. A green count of 77/81 is the expected state; 81/81 would
# mean somebody implemented work that is not authorised.
#
# `verifier/test_publication_override.py` HAS NO DELIBERATE REDS. 61/61 green is its
# expected state, as of the R-A018-18 repair ruled at D-083(c); the two reds this block
# used to be read alongside -- the unexamined-credential pair -- are CLOSED, not
# reserved. See `check_owner_override`, which now runs on every path a bundle carrying
# a §5.5 credential is presented for. A red in that file is now a regression.
#
#   R-A018-04 (DEFERRED: needs live chain state, and no chain is named yet)
#     TestDeploymentIdentityIsNotBound
#       .test_a_fabricated_runtime_code_hash_is_echoed_as_authenticated
#       .test_two_contradictory_manifests_cannot_both_certify
#       .test_the_result_names_the_block_its_claims_are_true_at
#     Closing these means comparing the manifest's runtimeCodeHash against live
#     deployed bytecode or an authenticated state proof at a named block. The
#     mitigation actually shipped here is narrower and is stated rather than
#     implied: NOT_ESTABLISHED below, printed beside every result, says the field
#     is an authority assertion and nothing more.
#
#     THE CLASS'S FOURTH TEST IS GREEN, AND HOW THIS BLOCK SAYS SO IS ITSELF THE
#     LESSON. `.test_an_offline_run_does_not_certify_an_authenticated_deployment`
#     was recorded here as passing "incidentally" -- no banner is printed under
#     --evaluation-time at all, so the string it forbade was unreachable. That
#     parenthesis was an honest label on a test that asserted nothing, and being
#     declared is what made the hole easy to stop looking at: it stood for hours.
#     The test now stages a LIVE-CLOCK CERTIFYING run and asserts that the banner
#     which really is printed claims no authenticated deployment. It passes for a
#     reason. No chain binding exists either way, which is why the three above stay
#     red and this one is not evidence for them.
#
#   R-A018-17 (RULED disclosed-only by John at D-083(b). PERMANENTLY RED BY RULING --
#              not pending, not deferred, and not a scope question still open.)
#     TestExactActionIsEnforced.test_calldata_redirecting_the_mandated_beneficiary_is_refused
#     Turning it green would mean decoding calldata against the mandated selector
#     inside this verifier, and D-083(b) ruled that this verifier decodes nothing:
#     the isolated signer's evaluator decodes semantics, the Vault binds bytes, and
#     this tool says plainly that it binds bytes too.
#     THE COST WAS RECORDED WITH THE RULING, and is repeated where an implementer
#     meets it: beneficiary binding now rests ENTIRELY on the isolated signer
#     behaving correctly, with no independent downstream check -- which is the
#     assumption the Vault exists so as not to have to make. See check_exact_action()
#     and the fourth NOT_ESTABLISHED entry, which is how a recipient is told.


class VerificationError(ValueError):
    pass


# SentinelTypes.sol: enum Verdict { BLOCK, REVIEW, ALLOW }.
BLOCK, REVIEW, ALLOW = 0, 1, 2
VERDICT_NAMES = {BLOCK: "BLOCK", REVIEW: "REVIEW", ALLOW: "ALLOW"}

AUTOMATIC_PATH = "automatic"
OVERRIDE_PATH = "owner-override"

# `verify()` reports which of these it produced; `main()` maps them to exit
# codes.  There is no mode in which this tool certifies executability -- see the
# module docstring.
MODE_STATIC = "offline-static-authenticity"
MODE_DIAGNOSTIC = "non-certifying-diagnostic"

NOT_ESTABLISHED = (
    "live code identity: no chain was read and no state proof was checked, so the "
    "manifest's runtimeCodeHash is authenticated only as an authority assertion (R-A018-04)",
    "nonce freshness: only the Vault consumes an action nonce, atomically, at execution; "
    "an offline run cannot establish that this nonce is unspent (R-A018-02)",
    "a trusted time source: the validity windows below were evaluated against a clock this "
    "tool does not authenticate, not an authenticated block timestamp (R-A018-03)",
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
    # bytes, and this tool binds bytes and says so.  The cost was recorded with the
    # ruling rather than argued away -- beneficiary binding rests entirely on the
    # isolated signer behaving correctly, with no independent downstream check --
    # which makes this entry the whole of what a recipient gets, and the reason it
    # is printed beside every certifying result rather than filed in a register.
    "conformance of the CALLDATA ARGUMENTS: the bytes are bound by dataHash and their "
    "leading selector is compared to the mandate, but nothing here decodes them, so a "
    "beneficiary, recipient or amount encoded inside callData is compared to no mandated "
    "value. Only the isolated signer's evaluator decodes them, and by ruling nothing "
    "downstream re-checks it (R-A018-17, disclosed-only)",
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
    inside `callData` is not compared to `mandate.beneficiary`.  That is R-A018-17,
    and it is SETTLED rather than pending -- D-083(b) ruled the binding
    disclosed-only, so this function will not grow a decoder and the frozen
    contract's `test_calldata_redirecting_the_mandated_beneficiary_is_refused` is
    permanently red by ruling.  The cost recorded with that ruling is that the
    beneficiary now rests on the isolated signer alone, with nothing downstream
    re-checking it; NOT_ESTABLISHED is where a recipient is told.
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

    operation = eip712.parse_uint("uint8", action["operation"])
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

    mandate = read_json(required(sample, "mandate.json"))
    policy = read_json(required(sample, "policy.json"))
    action = read_json(required(sample, "action.json"))
    receipt_doc = read_json(required(sample, "receipt.json"))
    mandate_sig = read_json(required(sample, "mandate-signature.json"))
    evidence_raw = read_bytes(required(sample, "evidence.json"))
    canonical_file = read_bytes(required(sample, "evidence.canonical.json"))
    evidence_hash_file = read_bytes(required(sample, "evidence.hash")).decode().strip().lower()
    receipt = receipt_doc.get("receipt")
    receipt_signature = receipt_doc.get("signature")
    if not isinstance(receipt, dict) or not isinstance(receipt_signature, str):
        raise VerificationError("receipt.json must carry a signed decision receipt")

    domain = {
        "name": "Sentinel",
        "version": "0.3",
        "chainId": manifest["chainId"],
        "verifyingContract": manifest["vault"],
    }

    canonical = jcs.canonicalize(jcs.parse_bytes(evidence_raw))
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

    # THE VERDICT, BEFORE THE ACTION PREDICATE. Deliberate ordering: the corpus's
    # BLOCK bundles are blocked precisely BECAUSE their action does not match the
    # mandate, and a recipient handed `case-2-injection-block` should be told the
    # signer said BLOCK, not merely that a target field disagrees.
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

    result = {
        "mode": mode,
        "deploymentAuthority": authority.lower(),
        # Authenticated as an authority ASSERTION, not as a fact about a live
        # deployment: nothing here read a chain. R-A018-04 is open; see
        # NOT_ESTABLISHED, which is printed alongside this payload.
        "deploymentBlockNumber": manifest["deploymentBlockNumber"],
        "runtimeCodeHash": manifest["runtimeCodeHash"],
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
    compared = ("the action's target, value, selector and operation match the mandate and "
                "policy")
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
    print("NOT ESTABLISHED by this run: " + "; ".join(NOT_ESTABLISHED) + ".")
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
