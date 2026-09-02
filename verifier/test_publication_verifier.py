#!/usr/bin/env python3
"""Adversarial tests for the v0.3 publication predicate and deployment manifest.

    python3 verifier/test_publication_verifier.py
    python3 -m unittest discover -s verifier -v

WHY THIS FILE EXISTS
--------------------
`verifier/verify_publication.py` and `verifier/deployment.py` are the two files
commit `a38cff9` added, and they are the two files in `verifier/` that the
221-test suite never imports. The commit boundary, the coverage boundary and the
post-Gate-8 boundary coincide (a018-remediation-register.md §1.2). This file is
R-A018-06's direct adversarial coverage for both.

THIS FILE IS A CONTRACT, NOT A REGRESSION SUITE
-----------------------------------------------
It was written against the frozen baseline `952b665` (the register commit; the
code under test is unchanged since `a38cff9`) by an author who was forbidden to
edit either module — D-058(1), A-028. A large fraction of the tests below FAIL
on that baseline **by design**. They are the statement of what the predicate must
do, written before and independently of the implementation that will satisfy
them. A test here that goes green without a code change is testing something the
baseline already gets right; each such test says so in its own docstring.

Every failing test names the register item it discharges. Tests marked
EXTENSION are defects this author found that the register's §1 does not record;
they are flagged rather than smuggled in, because the register authorises
nothing and the scope of a repair batch is not a test author's call.

HOW A SIGNED DEPLOYMENT MANIFEST IS BUILT HERE, AND WHY THAT WAY
----------------------------------------------------------------
`deployment.verify` needs `keccak256(b"sentinel.deployment-manifest.v1\\n" +
jcs.canonicalize(payload))` signed by a secp256k1 key. The obvious routes are
`eth_account` (not installed) or viem under `ts/node_modules` (installed, but it
would make a Python unit test depend on a Node toolchain, a `node_modules` tree
that is not pinned — R-A018-13 — and a subprocess round trip per signature).

Neither is necessary. `verifier/secp256k1.py` already ships `sign_digest`, which
exists precisely so a test can mint a *valid but wrong-party* signature, and
`verifier/test_verifier.py` has signed with it since D-010. This file uses the
same primitive against the same keccak/JCS modules the verifier itself uses, so
the manifests here are byte-identical to the ones `cold-demo.ts` produces with
viem, and the suite has no dependency outside the standard library.

The deployment authority key is DERIVED, not literal: it is
`keccak256(b"sentinel/a018 test deployment authority") mod n`. That keeps a
64-hex private key out of the source (R-A018-12; and out of reach of the
`scripts/assemble-enforcement-release.py` fixed-key regex) while staying exactly
reproducible. Owner and signer keys are imported from `verify.py` rather than
restated, for the same reason.

A NOTE ABOUT THE CLOCK, AND THE TRAP IT LAID
--------------------------------------------
The fixture receipts carry a 300-second validity window that expired in the
past, so every bundle-level test must name an evaluation time. The only way to
do that is `verify(..., evaluation_time=...)` — the same caller-chosen clock
R-A018-03 exists to remove. That was never a contradiction: R-A018-03's closure
condition is that injected time "survives only in a non-certifying test mode
that cannot produce a certifying result", so a fixed implementation still needs
*some* named non-certifying evaluation path.

THAT PATH HAS NOW LANDED, and `_predicate()` stays pointed at it: a run under
`--evaluation-time` reports diagnostics, certifies nothing and exits 3.

It also took three tests down with it, silently. A test that asserts a property
OF a certifying run — what the PASS banner may claim — stops asserting anything
the moment the path it runs on can no longer certify. Two were guarded by
conditionals that stopped matching; one forbade a literal the module no longer
emits. All three stayed green. See `live_bundle()` and `certifying_run()`, which
stage the DEFAULT clock path so those properties have a witness again, and the
docstrings of the three repaired tests, which say what each had stopped testing.

The general lesson, for whoever adds the next test here: an assertion about
certifying output must be run on a bundle that certifies, and the run that
produces it must be asserted to have certified. `certifying_run()` does the
second part so it cannot be forgotten.

KNOWN BLIND SPOTS, RECORDED SO THE GREEN SUITE IS NOT READ AS MORE THAN IT IS
-----------------------------------------------------------------------------
* "changed target code" and "stale state proof" from R-A018-06's minimum
  negative set are NOT directly asserted. Neither module performs any RPC, so an
  offline test cannot witness live bytecode or a state proof. What is asserted
  instead is the weaker property that survives offline: a run that consulted no
  chain state must not PRESENT itself as having established one — it must name
  the chain it did not read, in the same output as the result
  (`TestDeploymentIdentityIsNotBound`). That is a disclosure test, not a binding
  test, and it is worth exactly what a disclosure is worth. When R-A018-04 lands
  with a real chain binding, both negatives still need writing against it, and
  the three deferred tests in that class are the placeholders.
* Nonce freshness is likewise unobservable offline (R-A018-02's "responsibility
  split"). This file asserts that the dead branch is gone, and that a certifying
  offline run states it cannot establish freshness; it cannot assert that a
  consumed nonce is detected.
* Nothing here tests the TypeScript runtime, the release digest (R-A018-07), or
  the cold demo's negative controls (R-A018-09).

A DECLARED BLIND SPOT IS STILL A BLIND SPOT
-------------------------------------------
The first two entries above were already written down when three tests in this
file quietly stopped asserting anything (see the clock note below). Being
declared did not make them coverage, and the declaration is what made the gap
easy to stop looking at: one of the three was named in
`verify_publication.py`'s KNOWN RED TESTS block as passing "incidentally", and
that was allowed to stand as the whole of the answer.

So each entry above now says which half of its item is asserted and which is
not, and the repaired tests assert the observable half rather than resting on
the label. Where a property really is unobservable offline it stays RED and
named, never green-and-explained.

THE D-086 / D-087 EXTENSION (2026-09-01, against frozen baseline `2115c4f`)
--------------------------------------------------------------------------
The contract was unfrozen by John at D-086 -- D-083(d)'s release condition
fired when Crucible Cycle 1 bound the `deployment.verify(evaluation_time=None)`
fail-open as a withdrawal condition (Binding Critical 2). This file was extended
under D-058(1) by an author again forbidden to edit either module. Every new
test says whether it FAILS on `2115c4f` (the implementer's contract) or PASSES
(already correct, held so it cannot regress). The classes, in file order:

* `TestTheCertifyingInstantIsNotOmissible` -- D-086(e): omitting the instant
  REFUSES with `DeploymentManifestError`, never skips the lifetime bound.
* `TestTheStaticResultDisclaimsWhatItDidNotAuthenticate` -- D-086(e): the
  static result disclaims deployment identity, nonce freshness, currentness
  and executability; injected time lives only in the non-certifying mode.
* `TestDeploymentIdentityIsNotBound` -- the three R-A018-04 reds RE-EXAMINED
  under the non-certifying-static route. What each became, and why, is in its
  own docstring; the class docstring carries the decision.
* `TestOperationIsCallUnconditionally` -- D-087(a): `SentinelVault.sol:357`
  requires `operation == CALL` whatever the policy says.
* `TestARefusalRecordIsRecognisedAndNotCertified` -- D-087(d): a §5.5.1 bundle
  is refused AS a refusal record, not as a missing receipt, and the refusal
  says this verifier does not certify refusals. The 32 refusal checks are
  deliberately NOT tested: the ruling is recognition, not verification.
* `TestTheVaultBackstopsAreDisclosed` -- D-087(a): `maxNativeValueWei`,
  `allowedTarget`, `allowedSelector` are Vault state this tool cannot reach,
  and NOT_ESTABLISHED must say so.
* `TestTheExecutabilityClaimIsStated` -- D-087(c): the A/B split is on the
  surface -- this tool certifies EXECUTABILITY, `verify.py` certifies
  AUTHENTICITY -- in the certifying output and in `--help`.

The twenty `deployment.verify(` call sites that passed no instant now go through
`verify_manifest()`, which names one. Only the omission tests call the module
directly. See that helper's docstring.
"""

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import deployment  # noqa: E402
import eip712  # noqa: E402
import jcs  # noqa: E402
import reasoncodes  # noqa: E402
import verify  # noqa: E402  (imported ONLY for its published test keys)
import verify_publication  # noqa: E402
from keccak import keccak256  # noqa: E402
from secp256k1 import (  # noqa: E402
    G, N, is_low_s, parse_signature, point_mul, public_key_to_address,
    recover_address, sign_digest,
)

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VERIFIER = os.path.join(REPO, "verifier")
SAMPLES = os.path.join(REPO, "fixtures", "samples")
PREDICATE = os.path.join(VERIFIER, "verify_publication.py")

# The published Anvil keys the D-010 suite already uses. Imported, never
# restated: a second copy of a private key in the tree is a second thing for
# R-A018-12's guard to find.
OWNER_KEY = verify._OWNER_TEST_KEY
SIGNER_KEY = verify._SENTINEL_SIGNER_TEST_KEY
OUTSIDER_KEY = verify._OUTSIDER_TEST_KEY

# Derived, not literal. See the module docstring.
AUTHORITY_KEY = int.from_bytes(
    keccak256(b"sentinel/a018 test deployment authority"), "big") % N
SECOND_AUTHORITY_KEY = int.from_bytes(
    keccak256(b"sentinel/a018 rotated deployment authority"), "big") % N


def address_of(key):
    return public_key_to_address(point_mul(key, G))


AUTHORITY = address_of(AUTHORITY_KEY)
OWNER = address_of(OWNER_KEY)
SIGNER = address_of(SIGNER_KEY)
OUTSIDER = address_of(OUTSIDER_KEY)

VAULT = "0xe7f1725e7734ce288f8367e1bb143e90bb3f0512"
CHAIN_ID = "31337"

# Inside every fixture receipt's [issuedAt, expiresAt) window. Fixed rather than
# relative so the suite is deterministic and does not silently start passing or
# failing as wall-clock time moves past the fixtures.
NOW = 1788059600

# Two decades, in seconds. Used as "unambiguously outside any sane manifest
# lifetime" so the tests do not legislate a particular bound.
TWO_DECADES = 20 * 365 * 24 * 3600

# For `Bundle.sync_projections`. Restated from `test_publication_conformance.py`
# rather than imported, because that file imports from this one and the import
# would be circular. Its `test_the_projection_resync_is_a_no_op_on_every_shipped_
# fixture` is what keeps the derivation honest; this copy must match it.
VERDICT_NAMES = {0: "BLOCK", 1: "REVIEW", 2: "ALLOW"}
EXPECTED_EFFECTS_FROM_MANDATE = (
    "target", "selector", "resourceId", "beneficiary", "durationSeconds", "recurringAllowed",
)


def read_json(*parts):
    with open(os.path.join(*parts), "rb") as handle:
        return json.loads(handle.read().decode("utf-8"))


def write_json(path, doc):
    with open(path, "w", encoding="ascii") as handle:
        json.dump(doc, handle)


def domain_of(payload):
    """The EIP-712 domain the predicate derives from the manifest.

    Restated here rather than imported so this file does not agree with
    `verify_publication` by construction: if the predicate changes which domain
    it builds, these signatures stop recovering and the tests say so.
    """
    return {
        "name": "Sentinel", "version": "0.3",
        "chainId": payload["chainId"], "verifyingContract": payload["vault"],
    }


def manifest_payload(**overrides):
    """A deployment payload describing the fixture deployment.

    `deploymentBlockHash`, `runtimeCodeHash`, `compilerMetadataHash` and
    `sourceArchiveHash` are INVENTED here, and that is the point: nothing in
    either module compares them to anything, so a fabricated value is echoed back
    inside a PASS payload as though it had been authenticated (register §1.1).
    """
    payload = {
        "schemaVersion": "1",
        "chainId": CHAIN_ID,
        "vault": VAULT,
        "owner": OWNER,
        "signer": SIGNER,
        "deploymentBlockNumber": "3",
        "deploymentBlockHash": "0x" + "a1" * 32,
        "runtimeCodeHash": "0x" + "b2" * 32,
        "compilerMetadataHash": "0x" + "c3" * 32,
        "sourceArchiveHash": "0x" + "d4" * 32,
        "issuedAt": str(NOW - 3600),
    }
    payload.update(overrides)
    return payload


def sign_manifest(payload, key=AUTHORITY_KEY):
    """Produce the signed manifest document `deployment.verify` expects."""
    digest = keccak256(deployment.DIGEST_TAG + jcs.canonicalize(payload))
    return {
        "schema": deployment.SCHEMA,
        "payload": payload,
        "authoritySignature": sign_digest(digest, key),
    }


def verify_manifest(document, authority=AUTHORITY, evaluation_time=NOW):
    """`deployment.verify` at a NAMED instant.

    D-086 makes the certifying instant non-omissible: a call that leaves
    `evaluation_time` out is REFUSED rather than allowed to skip the lifetime
    bound. Twenty call sites in this file used to omit it, none of them on
    purpose -- they were written before the bound existed and were never
    revisited when it did, which is exactly how the fail-open D-083(d) marked
    stayed reachable. Every site whose subject is something OTHER than the
    omission now goes through this helper; the tests whose subject IS the
    omission (`TestTheCertifyingInstantIsNotOmissible`) call
    `deployment.verify` directly, so the two cannot be confused.
    """
    return deployment.verify(document, authority, evaluation_time=evaluation_time)


class Bundle(object):
    """A staged publication bundle that can be tampered with and RE-SEALED.

    Re-sealing is the whole point, and it is the lesson `test_verifier.py`
    records at A-056: a mutation that leaves a stale hash or a stale signature is
    caught by the hash or signature check, and the binding the mutation was
    supposed to probe never bites. Every negative below therefore rebuilds the
    full chain --

        policy -> policyHash -> mandate -> mandateHash -> action -> actionHash
        -> receipt, then re-signs the mandate as the OWNER and the receipt as the
        SIGNER

    -- so what reaches the predicate is a perfectly authentic, internally
    consistent bundle that is nonetheless wrong. That is the position a
    third-party recipient is actually in, and it is the only position in which
    "the verifier checks the verdict / the target / the value" can be observed at
    all.

    `test_the_reseal_helper_produces_a_bundle_that_still_verifies` is the control
    that keeps this class honest.
    """

    def __init__(self, case, root, payload=None):
        self.payload = manifest_payload() if payload is None else payload
        self.dir = os.path.join(root, os.path.basename(case))
        shutil.copytree(os.path.join(SAMPLES, case), self.dir)
        self.mandate = read_json(self.dir, "mandate.json")
        self.policy = read_json(self.dir, "policy.json")
        self.action = read_json(self.dir, "action.json")
        self.receipt_doc = read_json(self.dir, "receipt.json")
        # `.get`, not `[]`: a §5.5.1 refusal bundle carries no `receipt` member
        # at all (`refusal-vault-paused`), and D-087(d)'s tests stage one
        # unsealed. `seal()` still indexes it, so a refusal bundle cannot be
        # re-sealed -- which is right, there is no receipt to re-sign.
        self.receipt = self.receipt_doc.get("receipt")
        self.evidence = read_json(self.dir, "evidence.json")
        self.owner_key = OWNER_KEY
        self.signer_key = SIGNER_KEY

    def path(self, name):
        return os.path.join(self.dir, name)

    def seal(self):
        """Re-seal the hash chain. Does NOT touch `evidence.json`; see below."""
        return self._seal_chain()

    def seal_resynced(self):
        """Re-seal with the §5.6 projections resynced to the documents first.

        THE STAGING DEFECT THIS CLOSES, and why it is a SEPARATE method. `seal()`
        rebuilds the chain and re-signs, and it never touched `evidence.json`.
        That was invisible while the verifier hashed the evidence and never
        opened it; the §5.6 projection arm (D-087(a), O2) opens it, and a
        bundle whose windows `live_bundle()` moved then carries an
        `evidence.normalizedAction` restating the OLD mandateHash, policyHash
        and deadline -- refused, correctly, for describing a call the bundle
        does not carry. The inventory diff's §3 warned of exactly this
        ("`Bundle.seal` does not resync them, and the first run produced three
        false positives from that").

        NOT folded into `seal()`: `ConformanceBundle.seal(documents, evidence)`
        stages its negatives as seal -> resync -> MUTATE -> write evidence ->
        seal, calling the base `seal()` with no argument at both ends. A resync
        inside the base seal would silently undo every mutation on the second
        pass and turn all of them into false greens; a keyword on the base
        seal collides with that subclass's own signature (measured: four
        `TypeError`s). So this is its own method, which that subclass does not
        override, and only the callers staging an internally-perfect live
        bundle use it. A test that mutates a projection must not.
        """
        self._seal_chain()               # the chain, so the projections have final hashes
        self.sync_projections()
        self.write_evidence()
        return self._seal_chain()        # re-signed over the final evidenceHash

    def sync_projections(self):
        """Derive every §5.6 projection and the reason-code commitment.

        Mirrors `ConformanceBundle.sync_projections` verbatim (see the note at
        `VERDICT_NAMES`): `normalizedAction` is the §5.3 ActionPayload plus
        `callData`; `expectedEffects` is six mandate fields, one policy field
        and the LOWER native ceiling (§5.2); `anchor` is the receipt's
        simulation block; `verdict` is the receipt's enum spelled out.
        """
        normalized = {name: self.action[name] for _, name in eip712.ACTION_FIELDS}
        normalized["callData"] = self.action["callData"]
        self.evidence["normalizedAction"] = normalized

        effects = {name: self.mandate[name] for name in EXPECTED_EFFECTS_FROM_MANDATE}
        effects["maxAllowanceIncreaseBaseUnits"] = self.policy["maxAllowanceIncreaseBaseUnits"]
        effects["maxNativeValueWei"] = str(min(int(self.mandate["maxNativeValueWei"]),
                                               int(self.policy["maxNativeValueWei"])))
        self.evidence["expectedEffects"] = effects

        self.evidence["anchor"] = {
            "blockNumber": self.receipt["simulationBlockNumber"],
            "blockHash": self.receipt["simulationBlockHash"],
        }
        self.evidence["verdict"] = VERDICT_NAMES[int(self.receipt["verdict"])]
        self.receipt["reasonCodesHash"] = reasoncodes.reason_codes_hash_hex(
            self.receipt_doc["reasonCodes"])

    def write_evidence(self):
        canonical = jcs.canonicalize(self.evidence)
        write_json(self.path("evidence.json"), self.evidence)
        with open(self.path("evidence.canonical.json"), "wb") as handle:
            handle.write(canonical)
        with open(self.path("evidence.hash"), "w", encoding="ascii") as handle:
            handle.write("0x" + keccak256(canonical).hex())
        self.receipt["evidenceHash"] = "0x" + keccak256(canonical).hex()

    def _seal_chain(self):
        domain = domain_of(self.payload)
        policy_hash = "0x" + eip712.policy_hash(self.policy).hex()
        self.mandate["policyHash"] = policy_hash
        mandate_hash = "0x" + eip712.mandate_hash(self.mandate).hex()
        self.action["policyHash"] = policy_hash
        self.action["mandateHash"] = mandate_hash
        self.action["dataHash"] = "0x" + keccak256(
            eip712.hex_to_bytes(self.action["callData"])).hex()
        action_hash = "0x" + eip712.action_hash(self.action).hex()
        self.receipt["policyHash"] = policy_hash
        self.receipt["mandateHash"] = mandate_hash
        self.receipt["actionHash"] = action_hash

        write_json(self.path("mandate.json"), self.mandate)
        write_json(self.path("policy.json"), self.policy)
        write_json(self.path("action.json"), self.action)
        self.receipt_doc["receipt"] = self.receipt
        self.receipt_doc["signature"] = sign_digest(
            eip712.receipt_digest(domain, self.receipt), self.signer_key)
        write_json(self.path("receipt.json"), self.receipt_doc)
        write_json(self.path("mandate-signature.json"), {
            "ownerAddress": address_of(self.owner_key),
            "ownerSignature": sign_digest(
                eip712.mandate_digest(domain, self.mandate), self.owner_key),
        })
        return self

    def manifest_file(self, key=AUTHORITY_KEY):
        path = os.path.join(os.path.dirname(self.dir), "deployment-manifest.json")
        write_json(path, sign_manifest(self.payload, key))
        return path


class PublicationTestCase(unittest.TestCase):
    """Staging, invocation, and the two assertion helpers everything else uses."""

    def setUp(self):
        self.root = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.root)

    def bundle(self, case="case-1-allow", payload=None, seal=True):
        room = tempfile.mkdtemp(dir=self.root)
        b = Bundle(case, room, payload=payload)
        return b.seal() if seal else b

    def live_bundle(self, case="case-1-allow", **manifest_overrides):
        """A bundle current at the REAL host clock, so a run can CERTIFY.

        `manifest_overrides` are applied to the manifest payload on top of the
        live `issuedAt`, so a certifying run can be staged under a manifest
        that differs in one named field (D-086(e): two contradictory
        `runtimeCodeHash` values, both authority-signed).

        THIS HELPER EXISTS BECAUSE THREE TESTS IN THIS FILE WENT VACUOUS.

        Every other bundle-level test names an `--evaluation-time`, and under
        the current implementation that flag puts the run in `MODE_DIAGNOSTIC`:
        it prints findings, certifies nothing and exits 3. That is the correct
        answer to R-A018-03 -- but it means the CERTIFYING banner is no longer
        reachable on that path at all, and three tests that asserted properties
        OF that banner stopped asserting anything without going red:

          * `TestClaimsMatchBehaviour.test_the_pass_line_does_not_overstate`
            was guarded by `if completed.returncode == 0`, which is now never
            taken. It is R-A018-08's only PASS-line witness, so that register
            row had no coverage at all.
          * `TestNonceCheckIsNotDead.test_an_offline_run_does_not_claim_nonce_freshness`
            and
            `TestDeploymentIdentityIsNotBound.test_an_offline_run_does_not_certify_an_authenticated_deployment`
            still ran their assertions, but against output that structurally
            cannot contain the banner they forbid.

        The certifying path is the DEFAULT clock path, and the fixtures cannot
        reach it: their receipt, mandate, policy and deadline windows all closed
        in the past. So a certifying run has to be STAGED -- every window moved
        around `time.time()` and the whole chain re-sealed, exactly as the
        override suite's `OverrideTestCase.live_bundle` does for its own arm.

        The manifest's `issuedAt` moves too: `deployment.check_lifetime` now
        judges it against the same instant, so a fixture-dated manifest would be
        refused as stale before the banner was ever printed.

        A test built on this helper is time-dependent in one direction only: it
        needs `time.time()` to be roughly now, which is the same assumption
        `verify()`'s default branch itself makes.
        """
        live = int(time.time())
        overrides = dict(manifest_overrides)
        overrides.setdefault("issuedAt", str(live - 60))
        b = self.bundle(case, payload=manifest_payload(**overrides), seal=False)
        b.receipt["issuedAt"] = str(live - 60)
        b.receipt["expiresAt"] = str(live + 3600)
        b.mandate["validAfter"] = str(live - 3600)
        b.mandate["validUntil"] = str(live + 7200)
        b.policy["validAfter"] = str(live - 3600)
        b.policy["validUntil"] = str(live + 7200)
        b.action["deadline"] = str(live + 7200)
        # The projections restate mandateHash, policyHash and deadline, all of
        # which just moved. See `Bundle.seal`.
        return b.seal_resynced()

    def certifying_run(self, case="case-1-allow", **manifest_overrides):
        """Run the CLI on a live-clock bundle and insist that it certified.

        The positive control for every "the certifying banner must not say X"
        assertion below. Without it those assertions are green whenever the run
        fails for an unrelated reason -- which is precisely how the three tests
        named above became vacuous. Returns (completed, headline, payload).
        """
        completed = self.cli(self.live_bundle(case, **manifest_overrides))
        self.assertEqual(
            completed.returncode, 0,
            "positive control broken: a live-clock bundle did not certify, so "
            "the banner assertions below would be vacuous.\n" + completed.stderr)
        lines = completed.stdout.splitlines()
        payload = json.loads(lines[-1])
        self.assertEqual(
            payload["mode"], verify_publication.MODE_STATIC,
            "exit 0 but not the certifying mode: " + repr(payload["mode"]))
        return completed, lines[0], payload

    def help_option(self, help_text, flag):
        """The help argparse prints FOR `flag` in its options list, or None.

        Not `flag in help_text`. `verify_publication.py`'s module docstring names
        `--evaluation-time` in prose and argparse reprints the docstring as the
        description, so a substring test over the whole of `--help` is satisfied
        even with `help=argparse.SUPPRESS` restored -- the state two tests here
        exist to forbid. A mutation run caught that; reading did not. What a
        reader looking for this tool's switches consults is the options list, so
        that is what is parsed.

        Returns the option's entry with whitespace normalised, so a caller can
        assert on what the flag SAYS as well as that it appears.
        """
        lines = help_text.splitlines()
        # Python 3.9 prints "optional arguments:"; 3.10+ prints "options:".
        header = [i for i, line in enumerate(lines)
                  if re.match(r"^(options|optional arguments):\s*$", line)]
        if not header:
            return None
        options = lines[header[0]:]
        entry = [i for i, line in enumerate(options)
                 if re.match(r"^\s+" + re.escape(flag) + r"\b", line)]
        if not entry:
            return None
        return " ".join("\n".join(options[entry[0]:]).split())

    def _predicate(self, bundle, authority=AUTHORITY, key=AUTHORITY_KEY,
                   evaluation_time=NOW, manifest_path=None):
        """Call the predicate at a named evaluation time.

        SEE THE MODULE DOCSTRING. `evaluation_time` is today's caller-chosen
        clock. When R-A018-03 replaces it with a named non-certifying mode, this
        one method is what needs repointing.
        """
        return verify_publication.verify(
            bundle.dir,
            manifest_path if manifest_path else bundle.manifest_file(key),
            authority, evaluation_time=evaluation_time)

    def assert_certifies(self, bundle, **kwargs):
        return self._predicate(bundle, **kwargs)

    def assert_refused(self, bundle, subject, **kwargs):
        """The predicate must refuse, AND the refusal must name `subject`.

        The message check is load-bearing, not decoration. Several repairs in
        this batch could make a bundle refuse for a reason unrelated to the
        defect the test is about -- a stricter clock, a chain binding that fails
        closed offline -- and a bare `assertRaises` would then go green while the
        check it was written for was still missing. Requiring the refusal to name
        its own subject is the house pattern from `test_verifier.py`
        ("must fail the receipt.evidenceHash check, not merely the file
        comparison").
        """
        with self.assertRaises((ValueError, KeyError)) as caught:
            self._predicate(bundle, **kwargs)
        message = str(caught.exception)
        self.assertRegex(
            message, subject,
            "refused, but not for the reason under test -- the refusal must "
            "name {!r}".format(subject))
        return message

    def cli(self, bundle, authority=AUTHORITY, key=AUTHORITY_KEY, extra=()):
        argv = [sys.executable, PREDICATE, bundle.dir,
                "--deployment-manifest", bundle.manifest_file(key),
                "--deployment-authority", authority] + list(extra)
        return subprocess.run(argv, capture_output=True, text=True)


# ---------------------------------------------------------------------------
# deployment.py -- authority selection and out-of-band trust
# ---------------------------------------------------------------------------

class TestDeploymentAuthority(PublicationTestCase):
    """`deployment.py` is where the recipient's out-of-band trust decision enters
    the system (register §1.2). Everything in this class PASSES on the baseline:
    the authority half of the module is the part that was built correctly, and
    saying so is as much a result as a failure is."""

    def test_a_manifest_verifies_under_the_authority_that_signed_it(self):
        """Control. Without this, every refusal below could be a broken fixture."""
        payload = manifest_payload()
        self.assertEqual(
            verify_manifest(sign_manifest(payload), AUTHORITY)["vault"], VAULT)

    def test_a_manifest_is_refused_under_any_other_authority(self):
        """PASSES on baseline. The recovered address is compared to the address
        the caller supplied, so a manifest signed by anyone else is refused even
        though its signature is perfectly valid."""
        with self.assertRaises(deployment.DeploymentManifestError) as caught:
            verify_manifest(sign_manifest(manifest_payload()), OUTSIDER)
        self.assertIn("expected out-of-band authority", str(caught.exception))

    def test_a_manifest_signed_by_an_outsider_is_refused(self):
        """PASSES on baseline. The mirror of the previous test: same expected
        authority, different signing key."""
        with self.assertRaises(deployment.DeploymentManifestError):
            verify_manifest(
                sign_manifest(manifest_payload(), OUTSIDER_KEY), AUTHORITY)

    def test_the_manifest_cannot_nominate_its_own_authority(self):
        """PASSES on baseline, and it is the single most important property in
        the module: a field the presenter adds naming itself as the trust root is
        rejected by the closed field set, so authority can only ever come from
        the caller's argument."""
        with self.assertRaises(deployment.DeploymentManifestError) as caught:
            verify_manifest(
                sign_manifest(manifest_payload(authority=OUTSIDER)), AUTHORITY)
        self.assertIn("authority", str(caught.exception))

    def test_the_expected_authority_argument_is_itself_validated(self):
        """PASSES on baseline. A caller who fat-fingers the out-of-band address
        must be told, not silently compared against a malformed string."""
        for bad in ("0x1234", "not-an-address", "0x" + "zz" * 20):
            with self.subTest(authority=bad):
                with self.assertRaises(deployment.DeploymentManifestError):
                    verify_manifest(sign_manifest(manifest_payload()), bad)


# ---------------------------------------------------------------------------
# deployment.py -- canonicalization
# ---------------------------------------------------------------------------

class TestDeploymentCanonicalization(PublicationTestCase):
    """The manifest digest is taken over RFC 8785 canonical bytes under a domain
    tag. Both halves are asserted; both PASS on the baseline."""

    def test_member_order_does_not_change_the_digest(self):
        """PASSES on baseline. JCS sorts, so a re-serialised manifest with its
        members in any order authenticates identically. Without this the digest
        would depend on whatever ordering the presenter's serialiser happened to
        emit."""
        payload = manifest_payload()
        reordered = dict(reversed(list(payload.items())))
        self.assertNotEqual(list(payload), list(reordered))
        self.assertEqual(deployment.digest(payload), deployment.digest(reordered))
        document = sign_manifest(payload)
        document["payload"] = reordered
        self.assertEqual(verify_manifest(document, AUTHORITY)["owner"], OWNER)

    def test_the_domain_tag_is_load_bearing(self):
        """PASSES on baseline. A signature over the bare canonical payload -- the
        same bytes without `sentinel.deployment-manifest.v1\\n` -- must not
        authenticate, or a signature harvested from any other protocol that
        happens to sign JCS bytes could be replayed as a deployment manifest."""
        payload = manifest_payload()
        untagged = sign_digest(keccak256(jcs.canonicalize(payload)), AUTHORITY_KEY)
        with self.assertRaises(deployment.DeploymentManifestError):
            verify_manifest(
                {"schema": deployment.SCHEMA, "payload": payload,
                 "authoritySignature": untagged}, AUTHORITY)

    def test_duplicate_members_are_refused_before_they_are_signed_over(self):
        """PASSES on baseline, via `jcs.parse_bytes`. A manifest whose raw JSON
        repeats a member has two readings; the one a human reads need not be the
        one that got signed. RFC 8785 3.1 forbids it and the parser enforces it."""
        raw = (b'{"schema":"' + deployment.SCHEMA.encode() +
               b'","payload":{"chainId":"1"},"payload":{"chainId":"31337"},'
               b'"authoritySignature":"0x00"}')
        with self.assertRaises(jcs.CanonicalizationError):
            jcs.parse_bytes(raw)


# ---------------------------------------------------------------------------
# deployment.py -- shape
# ---------------------------------------------------------------------------

class TestDeploymentShape(PublicationTestCase):
    """R-A018-06 says hostile coverage must be more than malformed JSON. It is
    still not less than malformed JSON. All of these PASS on the baseline."""

    def test_every_required_field_is_required(self):
        """PASSES on baseline. Field-by-field, because a closed set that happens
        to be enforced only in aggregate would drop the first omission."""
        for name in sorted(deployment.FIELDS):
            with self.subTest(missing=name):
                payload = manifest_payload()
                del payload[name]
                with self.assertRaises(deployment.DeploymentManifestError) as c:
                    verify_manifest(sign_manifest(payload), AUTHORITY)
                self.assertIn(name, str(c.exception))

    def test_an_unknown_field_is_refused(self):
        """PASSES on baseline."""
        with self.assertRaises(deployment.DeploymentManifestError):
            verify_manifest(
                sign_manifest(manifest_payload(surprise="0x00")), AUTHORITY)

    def test_the_document_shape_is_exact(self):
        """PASSES on baseline. Extra or missing top-level members are refused, so
        nothing can ride alongside the three that are checked."""
        for mutate in (
            lambda d: dict(d, note="hello"),
            lambda d: {k: v for k, v in d.items() if k != "authoritySignature"},
            lambda d: {k: v for k, v in d.items() if k != "payload"},
        ):
            with self.subTest(shape=mutate({"schema": 1, "payload": 1,
                                            "authoritySignature": 1}).keys()):
                with self.assertRaises(deployment.DeploymentManifestError):
                    verify_manifest(
                        mutate(sign_manifest(manifest_payload())), AUTHORITY)

    def test_a_foreign_schema_string_is_refused(self):
        """PASSES on baseline."""
        document = sign_manifest(manifest_payload())
        document["schema"] = "sentinel.deployment-manifest.v2"
        with self.assertRaises(deployment.DeploymentManifestError):
            verify_manifest(document, AUTHORITY)

    def test_a_foreign_schema_version_is_refused(self):
        """PASSES on baseline."""
        with self.assertRaises(deployment.DeploymentManifestError):
            verify_manifest(
                sign_manifest(manifest_payload(schemaVersion="2")), AUTHORITY)

    def test_uint_fields_reject_non_canonical_decimals(self):
        """PASSES on baseline. Leading zeros, hex, unicode digits and signs are
        all rejected -- two spellings of one number would be two digests over one
        fact."""
        for name in ("chainId", "deploymentBlockNumber", "issuedAt"):
            for bad in ("0123", "0x10", "1٢", "１２", "-1", "1 ", " 1", ""):
                with self.subTest(field=name, value=bad):
                    with self.assertRaises(deployment.DeploymentManifestError):
                        verify_manifest(
                            sign_manifest(manifest_payload(**{name: bad})), AUTHORITY)

    def test_address_fields_reject_wrong_widths_and_non_hex(self):
        """PASSES on baseline."""
        for name in ("vault", "owner", "signer"):
            for bad in ("0x" + "11" * 19, "0x" + "11" * 21, "0x" + "zz" * 20,
                        "11" * 20, 42, None):
                with self.subTest(field=name, value=bad):
                    with self.assertRaises(deployment.DeploymentManifestError):
                        verify_manifest(
                            sign_manifest(manifest_payload(**{name: bad})), AUTHORITY)

    def test_bytes32_fields_reject_wrong_widths_and_non_hex(self):
        """PASSES on baseline."""
        for name in ("deploymentBlockHash", "runtimeCodeHash",
                     "compilerMetadataHash", "sourceArchiveHash"):
            for bad in ("0x" + "aa" * 31, "0x" + "aa" * 33, "0x" + "gg" * 32, ""):
                with self.subTest(field=name, value=bad):
                    with self.assertRaises(deployment.DeploymentManifestError):
                        verify_manifest(
                            sign_manifest(manifest_payload(**{name: bad})), AUTHORITY)

    def test_a_non_object_payload_is_refused(self):
        """PASSES on baseline."""
        for payload in ([], "payload", 7, None):
            with self.subTest(payload=payload):
                with self.assertRaises(deployment.DeploymentManifestError):
                    verify_manifest(
                        {"schema": deployment.SCHEMA, "payload": payload,
                         "authoritySignature": "0x" + "11" * 65}, AUTHORITY)

    def test_a_malformed_signature_is_refused_rather_than_raised_through(self):
        """PASSES on baseline. Callers catch `DeploymentManifestError`; a bare
        `ValueError` from `bytes.fromhex` escaping the module would bypass every
        caller's refusal path."""
        for bad in ("0x" + "11" * 64, "0x" + "11" * 66, "0xzz", "", "0x"):
            with self.subTest(signature=bad):
                document = sign_manifest(manifest_payload())
                document["authoritySignature"] = bad
                with self.assertRaises(deployment.DeploymentManifestError):
                    verify_manifest(document, AUTHORITY)


# ---------------------------------------------------------------------------
# deployment.py -- lifetime, rotation, revocation
# ---------------------------------------------------------------------------

class TestDeploymentManifestLifetime(PublicationTestCase):
    """Register §1.5: `issuedAt` is validated as a canonical decimal and NEVER
    compared to anything. Two hits in the file, both structural. A signed
    manifest is therefore valid forever and there is no revocation path.

    On revocation specifically, and stated plainly rather than faked: a genuine
    revocation check needs an authenticated revocation source -- a list, an
    on-chain registry, a state proof -- and neither module has one, so no offline
    test can witness it. The minimum viable form of revocation that IS observable
    offline is a bounded lifetime, which is what this class asserts. When
    R-A018-04 brings chain access, revocation needs its own tests against that.
    """

    def test_issued_at_is_compared_to_something(self):
        """FAILS ON BASELINE -- register §1.5 / R-A018-06 (stale deployment
        record). A manifest issued two decades before the evaluation time
        authenticates today exactly as a fresh one does.

        The bound is the implementer's to choose -- a `validUntil` in the payload,
        a caller-supplied maximum age, an authenticated block. This test only
        requires that twenty years is on the far side of it."""
        stale = manifest_payload(issuedAt=str(NOW - TWO_DECADES))
        bundle = self.bundle(payload=stale)
        self.assert_refused(bundle, r"(?i)issuedAt|stale|expir|age|old|manifest")

    def test_a_manifest_issued_after_the_evaluation_time_is_refused(self):
        """FAILS ON BASELINE -- R-A018-06 (stale deployment record), upper bound.
        §1.5 records that `issuedAt` is never compared downward; it is not
        compared upward either. A manifest claiming to have been issued two
        decades in the future authenticates now, which is the post-dating half of
        the same missing comparison and the half a lifetime bound alone would not
        catch."""
        future = manifest_payload(issuedAt=str(NOW + TWO_DECADES))
        bundle = self.bundle(payload=future)
        self.assert_refused(bundle, r"(?i)issuedAt|future|not yet|manifest")

    def test_a_superseded_manifest_cannot_certify_after_signer_rotation(self):
        """FAILS ON BASELINE -- R-A018-06 (rotation and revocation).

        The attack in its exact form. The deployment rotates its signer: a fresh
        manifest is issued naming signer S2. The old manifest, naming S1, is
        still a valid authority signature over a valid payload, and it is still
        the manifest that makes S1's year-old receipts certify. A recipient
        handed the old manifest and an old receipt gets a PASS, indefinitely,
        with no way to tell it has been superseded.

        `docs/enforcement-release-v0.3.md` claims "signer rotation revokes the
        active mandate" (R-A018-08). Whatever that is true of, it is not true of
        this path."""
        rotated = manifest_payload(
            signer=OUTSIDER, issuedAt=str(NOW - 60))  # the CURRENT deployment
        self.assertNotEqual(rotated["signer"], SIGNER)
        superseded = manifest_payload(issuedAt=str(NOW - TWO_DECADES))
        bundle = self.bundle(payload=superseded)
        self.assert_refused(bundle, r"(?i)issuedAt|stale|expir|rotat|supersed|manifest")

    def test_issued_at_is_bounded(self):
        """FAILS ON BASELINE -- EXTENSION (not in register §1).

        `_uint` places no ceiling on the value, so `issuedAt` accepts 10**40 --
        a timestamp roughly 10**32 years hence. Any downstream arithmetic on a
        manifest timestamp inherits an unbounded integer. A uint64 ceiling is the
        obvious bound; the test only requires that one exists."""
        with self.assertRaises(deployment.DeploymentManifestError):
            verify_manifest(
                sign_manifest(manifest_payload(issuedAt="1" + "0" * 40)), AUTHORITY)


# ---------------------------------------------------------------------------
# deployment.py -- signature canonical form
# ---------------------------------------------------------------------------

class TestDeploymentSignatureCanonicalForm(PublicationTestCase):
    """EXTENSION -- not in register §1.

    `verify.py` holds the receipt, the refusal record AND the override to EIP-2
    low-s with v in {27,28}, and `test_verifier.py::TestSignatureCanonicalForm`
    exists specifically to stop that rule being applied to one signature and not
    another: "there is no basis in §5 for one rule on one and none on the other,
    so the asymmetry was an omission rather than a decision."

    `verify_publication.py` and `deployment.py` apply it to NONE of their three
    signatures. That is the same omission, reintroduced in the newer module.
    """

    def malleate(self, signature):
        """(r, s, v) -> (r, n-s, v^1): the same authorization, reflected."""
        r, s, v = parse_signature(signature)
        self.assertTrue(is_low_s(s), "the fixture should start out canonical")
        return ("0x" + r.to_bytes(32, "big").hex()
                + (N - s).to_bytes(32, "big").hex()
                + bytes([{27: 28, 28: 27}[v]]).hex())

    def test_a_malleated_manifest_signature_recovers_the_same_authority(self):
        """The premise, and it PASSES on baseline because it is a fact about
        ECDSA rather than about this code. Recorded so the next test cannot be
        read as a test of signature parsing."""
        payload = manifest_payload()
        digest = deployment.digest(payload)
        document = sign_manifest(payload)
        malleated = self.malleate(document["authoritySignature"])
        self.assertNotEqual(malleated, document["authoritySignature"])
        self.assertEqual(recover_address(digest, malleated), AUTHORITY)

    def test_a_high_s_manifest_signature_is_refused(self):
        """FAILS ON BASELINE -- EXTENSION. Two byte-distinct documents carry one
        authority decision, so a manifest has no unique identity: any scheme that
        would later revoke or pin a manifest by the hash of its bytes can be
        evaded by presenting the reflection."""
        document = sign_manifest(manifest_payload())
        document["authoritySignature"] = self.malleate(document["authoritySignature"])
        with self.assertRaises(deployment.DeploymentManifestError) as caught:
            verify_manifest(document, AUTHORITY)
        self.assertRegex(str(caught.exception), r"(?i)low-s|canonical|EIP-2|malleab")

    def test_the_bundle_signatures_are_held_to_the_same_rule(self):
        """FAILS ON BASELINE -- EXTENSION. The owner's mandate signature and the
        signer's receipt signature go through the same unguarded
        `recover_address`. Held to the same rule as the manifest, and as the
        legacy verifier already holds their equivalents."""
        bundle = self.bundle()
        signature_doc = read_json(bundle.path("mandate-signature.json"))
        signature_doc["ownerSignature"] = self.malleate(signature_doc["ownerSignature"])
        write_json(bundle.path("mandate-signature.json"), signature_doc)
        self.assert_refused(bundle, r"(?i)low-s|canonical|EIP-2|malleab")


# ---------------------------------------------------------------------------
# deployment.py -- diagnostics
# ---------------------------------------------------------------------------

class TestDeploymentDiagnostics(PublicationTestCase):
    """EXTENSION -- not in register §1."""

    def test_a_field_error_is_not_reported_as_a_signature_error(self):
        """FAILS ON BASELINE -- EXTENSION.

        `verify` calls `digest(payload)`, which calls `validate_payload`, from
        inside the `try` that catches `ValueError` and re-raises as "deployment
        authority signature is invalid". So a manifest with a leading zero in
        `issuedAt` is reported to the recipient as

            deployment authority signature is invalid: issuedAt has a leading zero

        The refusal is correct; the diagnosis is not. A recipient told their
        out-of-band authority's signature failed will go and re-check the
        authority -- the one thing that was fine -- and this is a verifier whose
        entire value is telling an unaided reader what went wrong (Critical 2)."""
        with self.assertRaises(deployment.DeploymentManifestError) as caught:
            verify_manifest(
                sign_manifest(manifest_payload(issuedAt="0123")), AUTHORITY)
        message = str(caught.exception)
        self.assertIn("leading zero", message)
        self.assertNotIn("signature is invalid", message)


# ---------------------------------------------------------------------------
# verify_publication.py -- the control, and the structural layer
# ---------------------------------------------------------------------------

class TestPublicationControl(PublicationTestCase):
    """Nothing below means anything if the staging helper cannot produce a bundle
    the baseline accepts."""

    def test_the_reseal_helper_produces_a_bundle_that_still_verifies(self):
        """PASSES on baseline, and MUST keep passing. If a repair breaks this,
        every negative in this file has become unfalsifiable."""
        result = self.assert_certifies(self.bundle())
        self.assertEqual(result["deploymentAuthority"], AUTHORITY.lower())
        self.assertEqual(result["evaluationTime"], str(NOW))

    def test_the_reseal_is_faithful_to_the_shipped_fixture(self):
        """PASSES on baseline. Re-sealing an untouched bundle must reproduce the
        fixture's own action hash, or the helper is quietly building a different
        action than the corpus records."""
        original = read_json(SAMPLES, "case-1-allow", "receipt.json")["receipt"]
        self.assertEqual(
            self.assert_certifies(self.bundle())["actionHash"],
            original["actionHash"])


class TestPublicationRequiredArtifacts(PublicationTestCase):
    """"Absent mandate proof" from R-A018-06's minimum negative set, plus its
    neighbours. All PASS on the baseline."""

    def test_every_required_artifact_is_required(self):
        """PASSES on baseline. Deleting any one of the seven named artifacts is
        refused by name."""
        names = ("mandate.json", "policy.json", "action.json", "receipt.json",
                 "mandate-signature.json", "evidence.json",
                 "evidence.canonical.json", "evidence.hash")
        for name in names:
            with self.subTest(missing=name):
                bundle = self.bundle()
                os.remove(bundle.path(name))
                self.assert_refused(bundle, re.escape(name))

    def test_an_absent_mandate_proof_is_not_treated_as_agreement(self):
        """PASSES on baseline. The mandate proof file is required, and an empty
        or partial one is refused by shape rather than skipped -- absence is not
        agreement."""
        for doc in ({}, {"ownerAddress": OWNER}, {"ownerSignature": "0x00"},
                    {"ownerAddress": OWNER, "ownerSignature": "0x00", "x": 1}):
            with self.subTest(shape=sorted(doc)):
                bundle = self.bundle()
                write_json(bundle.path("mandate-signature.json"), doc)
                self.assert_refused(bundle, r"(?i)shape|signature|missing|owner")

    def test_a_receipt_without_a_signature_is_not_a_receipt(self):
        """PASSES on baseline. An unsigned decision claim is not a weaker
        receipt; nothing about it is authenticated."""
        for doc in ({"receipt": {}}, {"signature": "0x00"},
                    {"receipt": "not-an-object", "signature": "0x00"}):
            with self.subTest(shape=sorted(doc)):
                bundle = self.bundle()
                write_json(bundle.path("receipt.json"), doc)
                self.assert_refused(bundle, r"(?i)signed decision receipt")


class TestPublicationInternalBindings(PublicationTestCase):
    """The hash chain a bundle is held together by. All PASS on the baseline --
    this layer was built correctly and the negatives that follow it are the ones
    that were not."""

    def test_evidence_canonicalization_is_checked(self):
        """PASSES on baseline."""
        bundle = self.bundle()
        with open(bundle.path("evidence.canonical.json"), "ab") as handle:
            handle.write(b" ")
        self.assert_refused(bundle, r"(?i)canonicaliz")

    def test_the_published_evidence_hash_is_checked(self):
        """PASSES on baseline. Corrupts the PUBLISHED hash rather than the bytes,
        which is the only way to isolate "keccak256(canonical) == evidence.hash"
        -- the A-049 lesson from the legacy suite."""
        bundle = self.bundle()
        with open(bundle.path("evidence.hash"), "w") as handle:
            handle.write("0x" + "00" * 32 + "\n")
        self.assert_refused(bundle, r"(?i)evidence\.hash")

    def test_the_receipt_is_bound_to_its_evidence(self):
        """PASSES on baseline. A receipt re-signed over a different evidence hash
        is refused, so the receipt cannot be detached from the evidence it
        claims to have decided on."""
        bundle = self.bundle(seal=False)
        bundle.receipt["evidenceHash"] = "0x" + "11" * 32
        bundle.seal()
        self.assert_refused(bundle, r"(?i)evidenceHash")

    def test_a_swapped_mandate_is_refused(self):
        """PASSES on baseline. Substituting another sample's mandate breaks the
        receipt's mandateHash binding."""
        bundle = self.bundle()
        shutil.copy(os.path.join(SAMPLES, "case-4-review-failmode-review",
                                 "mandate.json"),
                    bundle.path("mandate.json"))
        self.assert_refused(bundle, r"(?i)mandateHash|policyHash")

    def test_altered_calldata_without_a_matching_hash_is_refused(self):
        """PASSES on baseline. R-A018-06 "altered calldata" in its cheap form:
        the presenter edits `callData` and forgets `dataHash`."""
        bundle = self.bundle(seal=False)
        bundle.seal()
        action = read_json(bundle.path("action.json"))
        action["callData"] = action["callData"][:-2] + "ff"
        write_json(bundle.path("action.json"), action)
        self.assert_refused(bundle, r"(?i)dataHash")

    def test_calldata_is_required(self):
        """PASSES on baseline. Without `callData` there is no exact call to
        verify, and the predicate says so rather than skipping the check."""
        bundle = self.bundle()
        action = read_json(bundle.path("action.json"))
        del action["callData"]
        write_json(bundle.path("action.json"), action)
        self.assert_refused(bundle, r"(?i)callData")


class TestPublicationDeploymentConfiguration(PublicationTestCase):
    """R-A018-06 "deployment configuration": the manifest supplies chain, vault,
    owner and signer, and every EIP-712 artifact must match. All PASS on the
    baseline -- this is the part `a38cff9` got right."""

    def test_a_bundle_for_another_chain_is_refused(self):
        """PASSES on baseline. Wrong chain, from R-A018-06's minimum set."""
        bundle = self.bundle(payload=manifest_payload(chainId="1"))
        self.assert_refused(bundle, r"(?i)chainId")

    def test_a_bundle_for_another_vault_is_refused(self):
        """PASSES on baseline. Wrong Vault, from R-A018-06's minimum set."""
        bundle = self.bundle(payload=manifest_payload(vault="0x" + "11" * 20))
        self.assert_refused(bundle, r"(?i)vault")

    def test_a_bundle_for_another_owner_is_refused(self):
        """PASSES on baseline. The manifest's owner is the trust anchor for the
        mandate; a bundle whose principal is someone else does not certify."""
        bundle = self.bundle(payload=manifest_payload(owner=OUTSIDER))
        self.assert_refused(bundle, r"(?i)principal|owner")

    def test_a_receipt_from_an_unapproved_signer_is_refused(self):
        """PASSES on baseline. "Unapproved signer" from R-A018-06's minimum set,
        in its sharp form: the receipt is re-signed by an outsider whose
        signature is perfectly valid and simply belongs to the wrong party."""
        bundle = self.bundle(seal=False)
        bundle.signer_key = OUTSIDER_KEY
        bundle.seal()
        self.assert_refused(bundle, r"(?i)signer")

    def test_a_mandate_signed_by_someone_other_than_the_owner_is_refused(self):
        """PASSES on baseline. The other half: a valid signature from a
        non-owner over the owner's mandate."""
        bundle = self.bundle(seal=False)
        bundle.owner_key = OUTSIDER_KEY
        bundle.seal()
        self.assert_refused(bundle, r"(?i)owner")

    def test_a_receipt_declaring_an_unapproved_signer_is_refused(self):
        """PASSES on baseline. Declaration and recovery are checked separately,
        so a receipt cannot name one signer and be signed by another."""
        bundle = self.bundle(seal=False)
        bundle.receipt["signer"] = OUTSIDER
        bundle.seal()
        self.assert_refused(bundle, r"(?i)signer")


# ---------------------------------------------------------------------------
# verify_publication.py -- THE VERDICT
# ---------------------------------------------------------------------------

class TestVerdictIsEnforced(PublicationTestCase):
    """R-A018-01, register §1.1. `verify_publication.py` never reads
    `receipt["verdict"]`. The whole file contains no occurrence of the word.

    `SentinelVault.sol` reverts `NotAllowVerdict` on the automatic path and
    `NotReviewVerdict` on the override path; the offline verifier that is
    supposed to tell a recipient what the Vault would do agrees with it on
    neither."""

    def test_a_signed_block_receipt_does_not_certify(self):
        """FAILS ON BASELINE -- R-A018-01, register §1.1.

        `verdict` 0 is BLOCK (`SentinelTypes.sol`: BLOCK, REVIEW, ALLOW). The
        baseline prints "PASS: authenticated deployment, owner mandate, exact
        action, and current receipt" and exits 0."""
        bundle = self.bundle(seal=False)
        bundle.receipt["verdict"] = "0"
        bundle.seal()
        self.assert_refused(bundle, r"(?i)verdict|BLOCK")

    def test_the_shipped_block_fixture_does_not_certify(self):
        """FAILS ON BASELINE -- R-A018-01, register §1.1, verbatim.

        No tampering at all. `case-2-injection-block` is the corpus's REAL PROMPT
        INJECTION case, shipped with `verdict` "0" and eleven reason codes
        including SIGNER_MANDATE_TARGET_MISMATCH. The publication verifier
        certifies it unmodified."""
        self.assert_refused(self.bundle("case-2-injection-block", seal=False),
                            r"(?i)verdict|BLOCK")

    def test_the_other_shipped_block_fixtures_do_not_certify(self):
        """FAILS ON BASELINE -- R-A018-01. Every BLOCK bundle in the corpus, not
        just the injection one, so a fix keyed to a single fixture cannot pass."""
        blocks = [e["id"] for e in read_json(SAMPLES, "index.json")
                  if e["verdict"] == "BLOCK" and not e.get("signerRefused")]
        self.assertGreaterEqual(len(blocks), 3, "expected several BLOCK fixtures")
        for case in blocks:
            with self.subTest(case=case):
                self.assert_refused(self.bundle(case, seal=False),
                                    r"(?i)verdict|BLOCK")

    def test_a_review_receipt_does_not_certify_without_an_override(self):
        """FAILS ON BASELINE -- R-A018-01 clause 2. REVIEW is the Vault's
        owner-override path; with no override presented there is nothing to
        certify, and the bundle must not pass as though it were an ALLOW."""
        bundle = self.bundle(seal=False)
        bundle.receipt["verdict"] = "1"
        bundle.seal()
        self.assertFalse(os.path.exists(bundle.path("override.json")))
        self.assert_refused(bundle, r"(?i)verdict|REVIEW|override")

    def test_the_shipped_review_fixture_does_not_certify(self):
        """FAILS ON BASELINE -- R-A018-01. `case-4-review-failmode-review` ships
        a REVIEW receipt and an override the publication predicate never reads."""
        self.assert_refused(
            self.bundle("case-4-review-failmode-review", seal=False),
            r"(?i)verdict|REVIEW|override")

    def test_an_out_of_range_verdict_does_not_certify(self):
        """FAILS ON BASELINE -- R-A018-01, fail-closed. A verdict outside
        {0,1,2} must fail closed rather than fall through an equality test for
        ALLOW that was never written."""
        bundle = self.bundle(seal=False)
        bundle.receipt["verdict"] = "7"
        bundle.seal()
        self.assert_refused(bundle, r"(?i)verdict")


# ---------------------------------------------------------------------------
# verify_publication.py -- THE EXACT ACTION
# ---------------------------------------------------------------------------

class TestExactActionIsEnforced(PublicationTestCase):
    """R-A018-05: the shipped predicate compares NONE of target, value,
    selector, operation or policy validity against the mandate or the policy. It
    nonetheless prints "exact action" on success.

    Every bundle in this class is internally perfect: correct hashes, valid
    owner signature, valid signer signature, current mandate, current receipt.
    The only thing wrong with each is the thing the predicate does not look at.
    """

    def test_an_action_against_a_target_the_mandate_does_not_name_is_refused(self):
        """FAILS ON BASELINE -- R-A018-05, "wrong target".

        `mandate.target` binds the call to one contract. The action here goes
        somewhere else entirely and certifies. This is the same defect
        `case-2-injection-block` records from the evaluator's side, where the
        signer emitted SIGNER_MANDATE_TARGET_MISMATCH and the publication
        verifier printed PASS."""
        bundle = self.bundle(seal=False)
        self.assertEqual(bundle.action["target"], bundle.mandate["target"])
        bundle.action["target"] = "0x" + "11" * 20
        bundle.seal()
        self.assert_refused(bundle, r"(?i)target")

    def test_an_action_exceeding_the_mandate_value_ceiling_is_refused(self):
        """FAILS ON BASELINE -- R-A018-05, "wrong value".

        `mandate.maxNativeValueWei` is 1e16. This action moves ~1e21 -- five
        orders of magnitude over -- and certifies. Register §1.6 records that the
        Vault mechanically custodies value and that
        `action.target.call{value: action.valueWei}(callData)` is the path."""
        bundle = self.bundle(seal=False)
        ceiling = int(bundle.mandate["maxNativeValueWei"])
        bundle.action["valueWei"] = str(ceiling * 100000)
        bundle.seal()
        self.assert_refused(bundle, r"(?i)value|wei|ceiling|maxNative")

    def test_an_action_exceeding_the_policy_value_ceiling_is_refused(self):
        """FAILS ON BASELINE -- R-A018-05, "wrong value" against the policy.
        Asserted separately from the mandate ceiling because the two are distinct
        limits and a repair could enforce one and not the other."""
        bundle = self.bundle(seal=False)
        ceiling = int(bundle.policy["maxNativeValueWei"])
        bundle.mandate["maxNativeValueWei"] = str(ceiling * 1000000)
        bundle.action["valueWei"] = str(ceiling * 100000)
        bundle.seal()
        self.assert_refused(bundle, r"(?i)value|wei|ceiling|policy")

    def test_calldata_carrying_a_selector_the_mandate_does_not_name_is_refused(self):
        """FAILS ON BASELINE -- R-A018-05, "wrong selector".

        `mandate.selector` is 0xc188528b. The calldata here invokes something
        else on the mandated target, with the mandated value, and certifies.
        `dataHash` is recomputed so the hash binding cannot mask it."""
        bundle = self.bundle(seal=False)
        self.assertTrue(bundle.action["callData"].startswith(
            bundle.mandate["selector"]))
        bundle.action["callData"] = "0xdeadbeef" + bundle.action["callData"][10:]
        bundle.seal()
        self.assert_refused(bundle, r"(?i)selector")

    def test_an_operation_the_policy_does_not_allow_is_refused(self):
        """FAILS ON BASELINE -- R-A018-05, "operation".

        `policy.allowedOperation` is "0" (CALL). Operation "1" is a different
        execution mode with a different blast radius, and it certifies."""
        bundle = self.bundle(seal=False)
        self.assertEqual(bundle.policy["allowedOperation"], "0")
        bundle.action["operation"] = "1"
        bundle.seal()
        self.assert_refused(bundle, r"(?i)operation")

    def test_an_expired_policy_is_refused(self):
        """FAILS ON BASELINE -- R-A018-05, "expired policy".

        `policy.validAfter`/`validUntil` are hashed into `policyHash` and are
        therefore authenticated -- and then never read. This policy expired one
        second before the evaluation time and certifies. The mandate's own window
        IS checked, five lines away, which is what makes this an omission rather
        than a design."""
        bundle = self.bundle(seal=False)
        bundle.policy["validAfter"] = "0"
        bundle.policy["validUntil"] = str(NOW - 1)
        bundle.seal()
        self.assert_refused(bundle, r"(?i)policy")

    def test_a_policy_that_is_not_yet_valid_is_refused(self):
        """FAILS ON BASELINE -- R-A018-05, the other end of the policy window."""
        bundle = self.bundle(seal=False)
        bundle.policy["validAfter"] = str(NOW + 3600)
        bundle.policy["validUntil"] = str(NOW + 7200)
        bundle.seal()
        self.assert_refused(bundle, r"(?i)policy")

    def test_a_policy_for_another_vault_is_refused(self):
        """PASSES on baseline. Included as the control that shows the policy IS
        compared to the manifest on identity, which is exactly why its silence on
        validity above is an omission and not a deliberate scope line."""
        bundle = self.bundle(seal=False)
        bundle.policy["vault"] = "0x" + "11" * 20
        bundle.seal()
        self.assert_refused(bundle, r"(?i)policy\.vault")

    def test_calldata_redirecting_the_mandated_beneficiary_is_refused(self):
        """PERMANENTLY RED BY RULING -- R-A018-17, D-083(b). Observes the defect
        that ruling left open, and is built so nothing ELSE can move it.

        Target, selector, value and operation all left exactly as mandated. Only
        the beneficiary word inside the calldata is replaced with an attacker
        address, the §5.6 projections are resynced so `evidence.normalizedAction`
        restates the redirected bytes (an honest dashboard of a dishonest call),
        and the signer's attested decoded record is left as shipped -- still
        naming the MANDATED beneficiary. That is the lying-signer shape: every
        hash binds, every signature recovers, the record conforms to the mandate
        under D-087(b)'s check, and only the bytes disagree. D-083(b) ruled this
        tool decodes nothing, so by ruling this bundle CERTIFIES, and
        NOT_ESTABLISHED is where a recipient is told.

        F-3 (2026-09-01). The previous body called `seal()` and left the
        projections stale, so the §5.6 arm refused the bundle on `dataHash`
        before the exact-action predicate ever ran. It stayed red only because
        that message happened not to match `beneficiar|callData|exact`; one
        wording change elsewhere would have flipped it green and the floors
        guard would have reported unauthorised work that never happened. The
        test had stopped observing R-A018-17.

        THREE OUTCOMES, THREE SIGNALS, so the floors guard can tell them apart:

        * RED  -- the bundle certifies. The ruled state. The failing assertion
                  names the register item and the ruling.
        * GREEN -- the refusal names the beneficiary. Somebody decoded calldata
                  against D-083(b); the guard reports "declared red now
                  PASSES", which is the alarm it exists to raise.
        * ERROR -- refused by any OTHER arm before the exact-action predicate.
                  Staging intercepted, as in F-3; raised as `RuntimeError`,
                  which the guard never accepts as a deliberate red."""
        bundle = self.bundle(seal=False)
        beneficiary = bundle.mandate["beneficiary"][2:]
        self.assertIn(beneficiary, bundle.action["callData"],
                      "fixture changed: the beneficiary is no longer in calldata")
        bundle.action["callData"] = bundle.action["callData"].replace(
            beneficiary, "00" * 16 + "deadbeef" * 1 + "00" * 0)
        self.assertEqual(len(bundle.action["callData"]),
                         len(read_json(SAMPLES, "case-1-allow",
                                       "action.json")["callData"]))
        attested = bundle.evidence["decodedSelectorAndParameters"]
        self.assertIn(beneficiary, json.dumps(attested).lower(),
                      "fixture changed: the attested record no longer names the "
                      "mandated beneficiary, so this is not the lying-signer shape")
        bundle.seal_resynced()

        try:
            result = self._predicate(bundle)
        except (ValueError, KeyError) as exc:
            if re.search(r"(?i)beneficiar", str(exc)):
                return  # GREEN, deliberately: see the docstring.
            raise RuntimeError(
                "STAGING INTERCEPTED (F-3): the redirected bundle was refused by an "
                "arm unrelated to R-A018-17 before the exact-action predicate ran, "
                "so this test is not observing the ruled-open defect: " + str(exc))

        self.assertNotEqual(
            result["verdict"], "ALLOW",
            "R-A018-17: a bundle whose calldata redirects the mandated beneficiary "
            "certified as ALLOW with an internally perfect chain and an attested "
            "record that still names the mandated party. This is the ruled-open "
            "defect -- D-083(b) rules this tool decodes no calldata and discloses "
            "it in NOT_ESTABLISHED -- and this test is PERMANENTLY RED BY RULING. "
            "Do not turn it green; a green here means calldata was decoded.")


# ---------------------------------------------------------------------------
# verify_publication.py -- validity windows
# ---------------------------------------------------------------------------

class TestValidityWindows(PublicationTestCase):
    """The mandate, receipt and deadline windows. All PASS on the baseline: this
    arithmetic is correct, and the defect next door is that the CALLER chooses
    the `now` it is evaluated against (`TestClockIsNotTheCallers`)."""

    def test_a_mandate_that_is_not_yet_valid_is_refused(self):
        """PASSES on baseline. "Future mandate" from R-A018-06's minimum set."""
        bundle = self.bundle(seal=False)
        bundle.mandate["validAfter"] = str(NOW + 3600)
        bundle.mandate["validUntil"] = str(NOW + 7200)
        bundle.seal()
        self.assert_refused(bundle, r"(?i)mandate is not current")

    def test_an_expired_mandate_is_refused(self):
        """PASSES on baseline. "Expired mandate" from R-A018-06's minimum set."""
        bundle = self.bundle(seal=False)
        bundle.mandate["validAfter"] = "0"
        bundle.mandate["validUntil"] = str(NOW - 1)
        bundle.seal()
        self.assert_refused(bundle, r"(?i)mandate is not current")

    def test_the_mandate_window_is_half_open(self):
        """PASSES on baseline. `validUntil` is exclusive: at exactly validUntil
        the mandate is over. Pinned because an off-by-one here silently extends
        every mandate by a second."""
        bundle = self.bundle(seal=False)
        bundle.mandate["validAfter"] = str(NOW)
        bundle.mandate["validUntil"] = str(NOW)
        bundle.seal()
        self.assert_refused(bundle, r"(?i)mandate is not current")

    def test_a_receipt_from_the_future_is_refused(self):
        """PASSES on baseline. "Future receipt" from R-A018-06's minimum set."""
        bundle = self.bundle(seal=False)
        bundle.receipt["issuedAt"] = str(NOW + 10)
        bundle.receipt["expiresAt"] = str(NOW + 1000)
        bundle.seal()
        self.assert_refused(bundle, r"(?i)receipt requires issuedAt")

    def test_an_expired_receipt_is_refused_at_the_evaluation_time(self):
        """PASSES on baseline AS AN ARITHMETIC CHECK ONLY, and that qualifier is
        the point. The comparison is right; register §1.1 records that a receipt
        which had expired hours earlier was revived by moving the evaluation time,
        so what this test establishes is narrower than it looks. The binding
        assertion is `TestClockIsNotTheCallers`."""
        bundle = self.bundle(seal=False)
        bundle.receipt["issuedAt"] = str(NOW - 1000)
        bundle.receipt["expiresAt"] = str(NOW - 1)
        bundle.seal()
        self.assert_refused(bundle, r"(?i)receipt requires issuedAt")

    def test_a_passed_action_deadline_is_refused(self):
        """PASSES on baseline."""
        bundle = self.bundle(seal=False)
        bundle.action["deadline"] = str(NOW - 1)
        bundle.seal()
        self.assert_refused(bundle, r"(?i)deadline")

    def test_a_post_hoc_edit_to_a_signed_time_field_is_refused(self):
        """PASSES on baseline.

        Every time field is inside a signed struct, so the presenter's only
        route to a non-canonical or widened value is to edit the JSON after the
        fact. That is what is staged here: a sealed bundle, then a direct file
        edit. The refusal comes from the hash binding or from
        `eip712.parse_uint`, and both are correct; what must not happen is the
        edit surviving.

        Deliberately NOT staged through `seal()`: `eip712` refuses to hash
        "0123" or "-1" at all, so a bundle carrying one cannot be constructed
        honestly. That refusal is itself the property, and it is the legacy
        suite's (`TestStrictFieldParsing`), not this file's."""
        edits = (
            ("mandate.json", "validUntil"),
            ("receipt.json", "expiresAt"),
            ("action.json", "deadline"),
        )
        for filename, field in edits:
            for bad in ("0123", "-1", "0x10", "999999999999999999999"):
                with self.subTest(field="{}.{}".format(filename, field),
                                  value=bad):
                    bundle = self.bundle()
                    doc = read_json(bundle.path(filename))
                    if filename == "receipt.json":
                        doc["receipt"][field] = bad
                    else:
                        doc[field] = bad
                    write_json(bundle.path(filename), doc)
                    with self.assertRaises((ValueError, KeyError)):
                        self._predicate(bundle)


# ---------------------------------------------------------------------------
# verify_publication.py -- the nonce
# ---------------------------------------------------------------------------

class TestNonceCheckIsNotDead(PublicationTestCase):
    """R-A018-02. The only nonce check in the file is

        if eip712.parse_uint("uint256", action["actionNonce"]) < 0:

    and `parse_uint` returns a non-negative int or raises, so the branch cannot
    fire. It reads as a freshness check and is not one.

    R-A018-02's corrected responsibility split says an offline verifier CANNOT
    consume the on-chain nonce -- so this class does not pretend to test
    detection of a consumed nonce. It tests the two things that are observable
    offline: that the dead branch is gone, and that an offline run does not
    claim the freshness it cannot establish."""

    def test_the_nonce_branch_is_provably_unreachable(self):
        """PASSES on baseline BY DESIGN -- it is the demonstration, not the
        contract. `parse_uint` raises on anything negative and returns a
        non-negative int otherwise, so no input reaches the `< 0` body. Recorded
        as executable evidence so the claim in R-A018-02 is not prose."""
        with self.assertRaises(eip712.EncodingError):
            eip712.parse_uint("uint256", "-1")
        for value in ("0", "1", str(2 ** 256 - 1)):
            self.assertGreaterEqual(eip712.parse_uint("uint256", value), 0)

    def test_the_dead_nonce_branch_is_gone(self):
        """FAILS ON BASELINE -- R-A018-02, first closure condition ("the dead
        branch is deleted").

        A source assertion, deliberately. The branch has no observable behaviour
        -- that is what is wrong with it -- so no input-driven test can witness
        its removal. Reading the shipped file is the only way to assert it, and
        the house already reads source and spec text for exactly this class of
        property (`TestPublishedTypeStrings`)."""
        with open(PREDICATE, "r", encoding="utf-8") as handle:
            source = handle.read()
        # assertFalse, not assertNotIn: assertNotIn would print the whole
        # module into the failure report.
        self.assertFalse(
            'parse_uint("uint256", action["actionNonce"]) < 0' in source,
            "verify_publication.py still contains the unreachable nonce branch "
            '`parse_uint("uint256", action["actionNonce"]) < 0` (R-A018-02)')
        self.assertFalse(
            re.search(r'parse_uint\(\s*"uint256"[^)]*\)\s*<\s*0', source),
            "verify_publication.py still compares an unsigned parse against 0")

    def test_an_offline_run_does_not_claim_nonce_freshness(self):
        """R-A018-02, second closure condition ("any offline-only mode must state
        it cannot establish nonce freshness and must not print 'current
        receipt'"). NOW GREEN.

        The baseline printed, on a run that opened no socket:
            PASS: authenticated deployment, owner mandate, exact action, and
            current receipt

        THIS TEST WAS VACUOUS AND IS REPAIRED HERE -- the same defect as the two
        in `TestClaimsMatchBehaviour` and `TestDeploymentIdentityIsNotBound`, and
        not caught by instrumentation because its assertion did execute. It ran
        under `--evaluation-time`, which now certifies nothing and prints no
        banner, and it forbade a literal ("current receipt") that no longer
        occurs anywhere in `verify_publication.py`. An assertion that cannot fail
        is not weaker coverage than one that can; it is none.

        The closure condition has two clauses and both are asserted, on the
        certifying default-clock path where the banner actually exists: the run
        must not claim receipt currency, and it must STATE that nonce freshness
        is not established. The second clause is the one that carries the item --
        R-A018-02's corrected responsibility split says an offline verifier
        cannot consume the on-chain nonce, so what is owed to a recipient is the
        admission, not the check."""
        completed, headline, payload = self.certifying_run()

        self.assertNotRegex(
            headline, r"(?i)current receipt|fresh nonce|unspent",
            "an offline certifying run claims a freshness it cannot establish: "
            + repr(headline))

        self.assertTrue(
            any(re.search(r"(?i)nonce", item)
                and re.search(r"(?i)cannot establish|unspent", item)
                for item in payload["notEstablished"]),
            "the result does not state that nonce freshness is unestablished: "
            + repr(payload["notEstablished"]))
        self.assertRegex(
            completed.stdout,
            r"(?i)offline run cannot establish that this nonce is unspent",
            "the human-readable output does not tell the recipient that the "
            "nonce may already have been consumed")


# ---------------------------------------------------------------------------
# verify_publication.py -- the clock
# ---------------------------------------------------------------------------

class TestClockIsNotTheCallers(PublicationTestCase):
    """R-A018-03, register §1.1. `--evaluation-time` is registered with
    `help=argparse.SUPPRESS`: a hidden flag that hands the caller the clock the
    module's own docstring says the presenter does not have.

    These assert at the CLI on purpose. R-A018-03's closure condition allows
    injected time to survive "in a non-certifying test mode that cannot produce a
    certifying result", so the stable contract is about what a certifying run
    emits, not about which keyword arguments exist."""

    def test_an_injected_clock_cannot_produce_a_certifying_result(self):
        """FAILS ON BASELINE -- R-A018-03, "refused clock override" from
        R-A018-06's minimum set.

        Baseline: exit 0 and the full PASS line. The receipt window in the
        fixtures closed long ago, so this run is certifying a receipt that is
        expired in every frame except the one the caller picked."""
        completed = self.cli(self.bundle(), extra=["--evaluation-time", str(NOW)])
        self.assertNotEqual(
            completed.returncode, 0,
            "an injected clock produced exit 0:\n" + completed.stdout)
        # `assertNotIn("PASS:", ...)` stood here and could not fail: the module
        # prints "PASS (static, offline):" and has never emitted the literal
        # "PASS:" on any path, so the check was satisfied by a spelling rather
        # than by behaviour. Matched loosely enough to catch the banner in any
        # of its wordings, and paired with the mode in the payload so a future
        # rewording cannot quietly restore certification here.
        self.assertNotRegex(
            completed.stdout, r"(?i)\bPASS\b",
            "a caller-chosen clock printed a PASS banner:\n" + completed.stdout)
        payload = json.loads(completed.stdout.strip().splitlines()[-1])
        self.assertEqual(
            payload["mode"], verify_publication.MODE_DIAGNOSTIC,
            "a run under --evaluation-time reported a certifying mode: "
            + repr(payload["mode"]))

    def test_an_injected_clock_cannot_revive_an_expired_receipt(self):
        """FAILS ON BASELINE -- R-A018-03, register §1.1 verbatim ("a receipt
        expired nine hours earlier was revived through --evaluation-time").

        The shipped fixture is used untouched: its receipt expired at
        1788059884, which is in the past by wall clock, and the flag alone puts
        it back inside its window."""
        expires = int(read_json(SAMPLES, "case-1-allow",
                                "receipt.json")["receipt"]["expiresAt"])
        self.assertLess(expires, int(time.time()),
                        "fixture receipt is not yet expired; this test is moot")
        completed = self.cli(self.bundle(), extra=["--evaluation-time", str(NOW)])
        self.assertNotEqual(completed.returncode, 0)

    def test_the_clock_control_is_not_concealed_from_the_help_text(self):
        """R-A018-03. NOW GREEN.

        A caller-facing switch that changes what the verifier certifies, hidden
        from `--help` by `argparse.SUPPRESS`, is not a debugging convenience: a
        recipient reading the interface cannot know the result they were handed
        was produced under a chosen clock. Either the flag is documented or it is
        gone; concealed is the one option that is not available.

        HARDENED, THOUGH NOT (YET) VACUOUS. The disjunction above is real and is
        kept, but it used to be spelled as a bare `if "evaluation-time" in
        source:` with nothing on the other side. That guard is true today, so
        this test is not among the three that emptied -- but it is the same
        shape, and one rename of the flag away from joining them. Written as an
        explicit `assertTrue(documented or gone)` it cannot go silently green in
        either direction.

        The `--help` half also now insists on argparse's OPTIONS LIST rather than
        any occurrence of the string. `verify_publication.py`'s module docstring
        mentions `--evaluation-time` in prose and argparse reprints it as the
        description, so a substring check over the whole of `--help` is satisfied
        with the flag fully suppressed -- which is the exact defect this test
        exists to catch. Found by mutation, not by reading."""
        completed = subprocess.run(
            [sys.executable, PREDICATE, "--help"], capture_output=True, text=True)
        with open(PREDICATE, "r", encoding="utf-8") as handle:
            source = handle.read()
        exists = "evaluation-time" in source
        documented = self.help_option(completed.stdout, "--evaluation-time") is not None
        self.assertTrue(
            documented or not exists,
            "--evaluation-time exists in the source and argparse's options list "
            "does not carry it: the switch is concealed, which is the one option "
            "R-A018-03 does not allow. A prose mention in the description is not "
            "documentation of a flag.\n" + completed.stdout)

    def test_a_certifying_run_reports_where_its_time_came_from(self):
        """FAILS ON BASELINE -- R-A018-03 ("an authenticated block timestamp or
        another explicitly trusted time source").

        The baseline's result payload carries `evaluationTime` and nothing about
        its provenance, so a recipient cannot distinguish a time read from an
        authenticated block from one typed on the command line. If a run
        certifies, the result must name its time source."""
        result = self._predicate(self.bundle())
        self.assertTrue(
            any("source" in key.lower() or "authenticated" in key.lower()
                for key in result),
            "certifying result names no time source: " + repr(sorted(result)))


# ---------------------------------------------------------------------------
# verify_publication.py -- deployment identity against live chain state
# ---------------------------------------------------------------------------

class TestDeploymentIdentityIsNotBound(PublicationTestCase):
    """R-A018-04, register §1.1. Neither module performs any RPC. The manifest's
    `runtimeCodeHash`, `deploymentBlockHash` and `compilerMetadataHash` are
    signed, validated for shape, and compared to nothing -- then echoed back
    inside the PASS payload, where they read as authenticated facts about a live
    deployment.

    THE THREE DELIBERATE REDS OF THIS CLASS WERE RE-EXAMINED UNDER D-086(e).
    Crucible Cycle 1 Binding Critical 2 is closed by the NON-CERTIFYING-STATIC
    route: the council said *"Live RPC is not mandatory if the bounded lab
    chooses the honest non-certifying path. What is mandatory is that the
    result stop claiming properties it did not authenticate"*, and John ruled
    that path taken, with live RPC NOT AUTHORISED. The three reds were written
    for the OTHER route -- each asserted a chain binding -- and against the
    ruled semantics each is now a test of work that is ruled out. Keeping them
    red would record "RPC is not built", which NOT_ESTABLISHED already says;
    it would not observe the defect the council actually bound, which is the
    CLAIM. So each was redefined to observe the claim:

    * `test_a_fabricated_runtime_code_hash_is_echoed_as_authenticated` keeps its
      name (it is the test the council will look for) and now asserts the
      ruled semantic directly: the value is never presented as an authenticated
      fact. GREEN-ABLE under the ruling.
    * `..._cannot_both_certify` became `..._both_authenticate_statically_and_
      neither_claims_deployment_identity`: with no chain, two contradictory
      manifests are two authentic authority assertions, and the honest result
      certifies both STATICALLY while claiming neither identity. GREEN-ABLE.
    * `..._names_the_block_its_claims_are_true_at` became `..._anchors_no_claim_
      to_a_block_and_says_executability_is_not_established`: with no
      executability claim there is no block to anchor one to, and a result that
      names one anyway is the overclaim in a new place. GREEN-ABLE.

    All three FAIL on `2115c4f`, because the baseline echoes `runtimeCodeHash`
    and `deploymentBlockNumber` as bare top-level facts of a certifying result
    and its NOT_ESTABLISHED list never uses the word "executability". None is
    a chain-binding test any more, and the class docstring's old claim that the
    three were "placeholders" for R-A018-04's binding is withdrawn: when a chain
    binding is authorised it needs NEW tests, not these.

    An offline test cannot check bytecode. What it CAN assert is the property
    R-A018-04 names: results must distinguish static authenticity from
    executability at a named block, so a run with no chain access must not emit
    an unqualified certification."""

    # A key under which an authority-asserted value may travel without reading
    # as a verified fact. The label has to SAY the value is asserted, claimed,
    # or unverified; a neutral container ("manifest", "deployment") does not,
    # because the manifest IS authenticated and a reader will assume its
    # contents are too -- which is the exact confusion R-A018-04 records.
    LABELLED = r"(?i)assert|unverified|unauthenticated|claim|said|disclaim|not.?established"

    @classmethod
    def paths_to(cls, node, needle, trail=()):
        """Every key path at which `needle` occurs as a string inside `node`."""
        found = []
        if isinstance(node, dict):
            for key, value in node.items():
                found.extend(cls.paths_to(value, needle, trail + (str(key),)))
        elif isinstance(node, list):
            for index, value in enumerate(node):
                found.extend(cls.paths_to(value, needle, trail + (str(index),)))
        elif isinstance(node, str) and needle.lower() in node.lower():
            found.append(trail)
        return found

    def assert_not_presented_as_a_fact(self, result, value, what):
        """`value` may be absent, or may appear only under a labelled key."""
        self.assertNotIn(
            what, result,
            "a certifying result carries a bare top-level {!r}: a value nothing "
            "verified, presented at the same level as the verdict, reads as an "
            "authenticated fact about the deployment (D-086(e))".format(what))
        # A plain loop, NOT `subTest`: this helper serves tests that are red on
        # the baseline, and `scripts/check-publication-suite-floors.sh` keys a
        # declared red on `test.id()`, which for a subTest failure carries a
        # "(path=...)" suffix the declaration's parser cannot name.
        unlabelled = ["/".join(trail) for trail in self.paths_to(result, value)
                      if not any(re.search(self.LABELLED, key) for key in trail)]
        self.assertEqual(
            unlabelled, [],
            "{!r} appears at {} under no label saying it is an authority "
            "assertion rather than a verified fact".format(value, unlabelled))

    def test_a_fabricated_runtime_code_hash_is_echoed_as_authenticated(self):
        """FAILS ON BASELINE -- R-A018-04 / Binding Critical 2, REDEFINED under
        D-086(e). The name is kept so the council can find the test that
        observes its finding; the body now asserts the ruled semantic.

        `runtimeCodeHash` here is 0xb2b2...b2, a value this test invented. On
        the baseline it appears verbatim as a top-level member of the certifying
        payload, beside `verdict` and `actionHash`, which are verified -- so a
        reader is handed one JSON object in which authenticated findings and an
        unchecked assertion are indistinguishable. D-086(e): *"a fabricated
        runtimeCodeHash is never reported as authenticated"*.

        What is required, on BOTH paths because the ruling says "never": the
        value is not a bare top-level member of the result, and wherever it does
        appear the key path says it is an assertion. Dropping it altogether also
        satisfies this. What is NOT required, by ruling: comparing it to a
        chain."""
        invented = "0x" + "b2" * 32
        self.assertEqual(manifest_payload()["runtimeCodeHash"], invented,
                         "fixture drift: the invented value moved")

        completed, headline, payload = self.certifying_run()
        self.assert_not_presented_as_a_fact(payload, invented, "runtimeCodeHash")
        self.assertNotRegex(
            headline, r"(?i)authenticated deployment|runtimeCodeHash",
            "the certifying headline presents the deployment identity as "
            "authenticated: " + repr(headline))

        diagnostic = self._predicate(self.bundle())
        self.assert_not_presented_as_a_fact(diagnostic, invented, "runtimeCodeHash")

    def test_two_contradictory_manifests_both_authenticate_statically_and_neither_claims_deployment_identity(self):
        """FAILS ON BASELINE -- R-A018-04, REDEFINED under D-086(e). Formerly
        `test_two_contradictory_manifests_cannot_both_certify`.

        Two manifests from the same authority, differing only in
        `runtimeCodeHash`, describe two different deployments; at most one is
        true of the chain. The old test demanded that at most one certify, which
        can only be met by reading the chain -- and D-086(e) rules live RPC NOT
        AUTHORISED. Under the ruled route both are authentic authority
        assertions and both certify STATICALLY; what the ruling forbids is
        either result CLAIMING the identity it did not check.

        So this test asserts the ruled behaviour in full: both runs certify
        (the positive control `certifying_run` insists on it -- a run that
        refused one of them would mean somebody built the chain binding this
        batch does not authorise); neither result presents its `runtimeCodeHash`
        as a fact; and each names deployment identity as NOT established, in
        the same payload, so a reader holding either one can see the
        contradiction is undetectable offline."""
        for invented in ("0x" + "11" * 32, "0x" + "22" * 32):
            completed, headline, payload = self.certifying_run(
                runtimeCodeHash=invented)
            self.assert_not_presented_as_a_fact(payload, invented, "runtimeCodeHash")
            self.assertTrue(
                any(re.search(r"(?i)deployment identity|code identity|"
                              r"deployed (byte)?code|what is deployed", item)
                    for item in payload["notEstablished"]),
                "the result certifies under manifest runtimeCodeHash {} whose "
                "code identity was compared to nothing and does not say so: "
                "{!r}".format(invented, payload["notEstablished"]))

    def test_an_offline_run_does_not_certify_an_authenticated_deployment(self):
        """R-A018-04 ("results distinguish static authenticity from
        executability at a named block"), the half that IS observable offline.
        NOW GREEN, and for a reason rather than incidentally.

        The baseline reached no network and printed "PASS: authenticated
        deployment, owner mandate, exact action, and current receipt" at exit 0.
        Whatever an offline run is entitled to say, it is not that.

        THIS TEST WAS VACUOUS AND IS REPAIRED HERE. It was the file's one
        DECLARED blind spot -- `verify_publication.py`'s KNOWN RED TESTS block
        records that it "now passes, but incidentally", because no PASS line is
        printed under `--evaluation-time` at all. An honest label on a test that
        asserts nothing is still a test that asserts nothing, and the assertion
        was doubly dead: it looked for the literal "PASS: authenticated
        deployment", a string this module cannot emit on any path, on a path
        where no banner is emitted at all.

        R-A018-04 splits cleanly, and the split is why this is repairable:

        * NOT observable offline, and still RED next door: whether the manifest's
          `runtimeCodeHash` is the code actually deployed. That needs live
          bytecode or a state proof, and it belongs to the three deferred tests
          in this class -- which stay red.
        * OBSERVABLE offline, and asserted here: that a run with no chain access
          does not PRESENT itself as having established one. The mitigation that
          actually shipped is a disclosure, so a disclosure is a thing a test can
          hold the module to.

        Repointed at the certifying default-clock path, because that is the only
        path where the module makes a claim capable of overstating."""
        completed, headline, payload = self.certifying_run()

        self.assertNotRegex(
            headline, r"(?i)authenticated deployment",
            "an offline run announces an authenticated DEPLOYMENT: "
            + repr(headline))

        # The NAME, anywhere in the payload -- not a top-level key. This used
        # to be `assertIn("runtimeCodeHash", payload)`, which required the bare
        # top-level echo that D-086(e) now forbids (see
        # `test_a_fabricated_runtime_code_hash_is_echoed_as_authenticated`).
        # What this test needs is only that the payload talks about the field.
        self.assertIn(
            "runtimeCodeHash", json.dumps(payload),
            "fixture drift: this test is about how runtimeCodeHash is presented")
        self.assertTrue(
            any(re.search(r"(?i)runtimeCodeHash", item)
                and re.search(r"(?i)no chain was read|authority assertion", item)
                for item in payload["notEstablished"]),
            "the result echoes runtimeCodeHash without saying, in the same "
            "payload, that no chain was read and the value is an authority "
            "assertion: " + repr(payload["notEstablished"]))

        self.assertRegex(
            completed.stdout,
            r"(?i)no chain was read and no state proof was checked",
            "the human-readable output does not tell the recipient that no "
            "chain state was consulted")
        self.assertRegex(
            payload["mode"], r"(?i)static",
            "a run that read no chain must name its mode as static rather than "
            "leaving executability implied: " + repr(payload["mode"]))

    def test_the_result_anchors_no_claim_to_a_block_and_says_executability_is_not_established(self):
        """FAILS ON BASELINE -- R-A018-04, REDEFINED under D-086(e). Formerly
        `test_the_result_names_the_block_its_claims_are_true_at`.

        The old test demanded that a certifying result name the block its
        executability claim is anchored to. Under the non-certifying-static
        route there is no executability claim, so there is nothing for a block
        to anchor: "names the block its claims are true at" has no meaning when
        the result claims nothing is true at any block. The honest inverse is
        what is asserted now.

        Two clauses. (1) The result must not anchor a claim to a block: no
        top-level key of the certifying payload may be a block field, because
        `deploymentBlockNumber` at the top level -- copied from the manifest,
        observed nowhere -- is the same overclaim as `runtimeCodeHash` beside
        the verdict. It may travel under a label that says it is asserted, as
        `assert_not_presented_as_a_fact` allows. (2) The result must SAY that
        executability is not established, in `notEstablished`, in that word.
        The baseline says it only inside `evaluationTimeSource`, a field about
        the clock, which is not where a reader looking for the executability
        claim will look."""
        completed, headline, payload = self.certifying_run()

        anchored = [key for key in payload if re.search(r"(?i)block", key)]
        self.assertEqual(
            anchored, [],
            "the certifying result carries a top-level block field {} while "
            "observing no block; a block a claim is 'true at' has no meaning "
            "when no executability claim is made (D-086(e))".format(anchored))
        block = manifest_payload()["deploymentBlockNumber"]
        unlabelled = ["/".join(trail) for trail in self.paths_to(payload, block)
                      if trail and re.search(r"(?i)block", trail[-1])
                      and not any(re.search(self.LABELLED, key) for key in trail[:-1])]
        self.assertEqual(
            unlabelled, [],
            "the manifest's block number appears at {} under no label saying "
            "it is an authority assertion".format(unlabelled))
        self.assertNotRegex(headline, r"(?i)\bblock\b",
                            "the headline anchors its claim to a block: "
                            + repr(headline))

        self.assertTrue(
            any(re.search(r"(?i)executab", item) for item in payload["notEstablished"]),
            "notEstablished never says EXECUTABILITY is not established; the "
            "word occurs only in evaluationTimeSource, which is about the clock: "
            + repr(payload["notEstablished"]))


# ---------------------------------------------------------------------------
# verify_publication.py -- what the tool says about itself
# ---------------------------------------------------------------------------

class TestClaimsMatchBehaviour(PublicationTestCase):
    """R-A018-08. Two of these are the register's own rows; the third is an
    overstatement in the module docstring that the register's table does not
    list."""

    def test_the_pass_line_does_not_overstate(self):
        """R-A018-08, the `verify_publication.py` row. NOW GREEN, and it is the
        register row's only witness, so what it asserts matters.

        The baseline printed one sentence carrying four claims: authenticated
        deployment (nothing was checked against chain state), owner mandate
        (true), exact action (target, value, selector and operation were
        unchecked), and current receipt (the caller chose the clock). Only one
        of the four held, and the line was printed for a BLOCK receipt.

        THIS TEST WAS VACUOUS AND IS REPAIRED HERE. It used to run under
        `--evaluation-time` behind `if completed.returncode == 0:`. That flag is
        now a non-certifying diagnostic that exits 3, so the guard was never
        taken and the two assertions never executed -- R-A018-08's PASS line had
        no coverage at all while the suite reported green. The banner is still
        reachable, just not there: it is on the DEFAULT clock path, which is why
        this now goes through `certifying_run()`.

        Four assertions, one per historical overclaim, each falsifiable by
        restoring the sentence it replaced:

        1. The run must SAY it is static and offline, so "PASS" is never read
           bare.
        2. It must not claim an authenticated DEPLOYMENT. What authenticates is
           the manifest -- a signed assertion by the out-of-band authority -- and
           the difference is the whole of R-A018-04.
        3. It must not claim an "exact action". It must instead ENUMERATE the
           fields it compared, because the arguments inside `callData` are not
           among them (R-A018-17).
        4. It must not claim a "current receipt", and it must name the clock its
           window findings were evaluated against as one it does not
           authenticate.

        Plus the standing obligation that makes the four survivable: everything
        the run did not establish is printed beside the banner, not buried."""
        completed, headline, payload = self.certifying_run()

        self.assertRegex(
            headline, r"(?i)\bstatic\b.*\boffline\b|\boffline\b.*\bstatic\b",
            "a certifying headline that does not qualify itself as static and "
            "offline reads as a statement about the live deployment: "
            + repr(headline))

        self.assertNotRegex(
            headline, r"(?i)authenticated deployment",
            "the headline claims an authenticated DEPLOYMENT; what was "
            "authenticated is the manifest, which is the authority's assertion "
            "ABOUT a deployment (R-A018-04): " + repr(headline))
        self.assertRegex(
            headline, r"(?i)manifest",
            "the headline must say it is the MANIFEST that authenticated: "
            + repr(headline))

        self.assertNotRegex(
            headline, r"(?i)exact action",
            "the headline still claims an 'exact action': " + repr(headline))
        for field in ("target", "value", "selector", "operation"):
            self.assertRegex(
                headline, r"(?i)\b" + field,
                "the headline claims the action conforms without naming {!r} as "
                "one of the fields actually compared, so a reader cannot tell "
                "what was left out (R-A018-17): {!r}".format(field, headline))

        self.assertNotRegex(
            headline, r"(?i)current receipt",
            "the headline claims a 'current receipt' while the clock it was "
            "judged at is unauthenticated: " + repr(headline))
        self.assertRegex(
            payload["evaluationTimeSource"], r"(?i)not an authenticated block",
            "a certifying result must name its time source as unauthenticated: "
            + repr(payload["evaluationTimeSource"]))

        self.assertIn(
            "NOT ESTABLISHED", completed.stdout,
            "the certifying run prints no NOT ESTABLISHED list, so every "
            "qualification above rests on the headline's wording alone")
        for topic in (r"(?i)no chain was read", r"(?i)nonce freshness",
                      r"(?i)trusted time source", r"(?i)CALLDATA ARGUMENTS"):
            self.assertRegex(completed.stdout, topic)

    def test_a_refusal_is_reported_on_stderr_with_a_nonzero_exit(self):
        """PASSES on baseline. The fail-closed plumbing works; a wrong
        out-of-band authority is refused, named, and exits 1."""
        completed = self.cli(self.bundle(), authority=OUTSIDER)
        self.assertEqual(completed.returncode, 1)
        self.assertIn("FAIL:", completed.stderr)
        self.assertIn("out-of-band authority", completed.stderr)
        self.assertEqual(completed.stdout, "")

    def test_the_module_does_not_claim_the_presenter_cannot_choose_the_clock(self):
        """EXTENSION (R-A018-08's table does not carry this row). NOW GREEN.

        On the baseline, `verify_publication.py`'s docstring -- which `argparse`
        reprints verbatim in `--help` -- said:

            "the presenter cannot choose either the deployment identity or the
             receipt clock"

        while the same `--help` output suppressed `--evaluation-time`. The claim
        and its own counterexample were printed by one command, and the reader
        was shown only the claim.

        THIS TEST WAS VACUOUS AND IS REPAIRED HERE. Its assertion sat behind

            if "evaluation-time" in source and
               "evaluation-time" not in completed.stdout:

        -- a guard that was true only while the flag was suppressed. The repair
        moved `--evaluation-time` into `--help`, which made the guard false, and
        the single assertion inside it has not executed since. The test went on
        reporting green on a body it never ran.

        Rewritten as an unconditional conjunction, because the property was never
        "the claim is absent WHEN the flag is hidden" -- it was that the tool must
        not tell a reader something its own interface contradicts. Three ways to
        break it, all asserted directly: re-add the sentence; re-suppress the
        flag; or document the flag without saying it cannot certify, which is the
        one fact that reconciles "the caller may choose a clock" with "a result
        you were handed was not produced under one"."""
        completed = subprocess.run(
            [sys.executable, PREDICATE, "--help"], capture_output=True, text=True)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        normalised = " ".join(completed.stdout.split())

        self.assertNotRegex(
            normalised, r"(?i)presenter cannot choose|cannot choose either",
            "--help still claims the presenter cannot choose the clock")
        self.assertNotRegex(
            normalised, r"(?i)cannot choose[^.]{0,80}clock",
            "--help still claims the presenter cannot choose the clock: "
            + repr(normalised[:400]))

        # THE OPTIONS LIST, NOT ANY MENTION. See `help_option`: a first draft
        # asserted `"--evaluation-time" in completed.stdout` and was defeated in
        # the falsification pass by the module docstring's prose mention, with
        # the flag fully suppressed from argparse.
        flag = self.help_option(completed.stdout, "--evaluation-time")
        self.assertIsNotNone(
            flag,
            "the counterexample is concealed again: --evaluation-time exists in "
            "the source and argparse's options list does not carry it, so a "
            "recipient reading the interface cannot learn the flag exists:\n"
            + completed.stdout)
        self.assertRegex(
            flag[:600], r"(?i)certif",
            "--help documents --evaluation-time without saying what it does to "
            "certification, which is the only thing that makes the flag safe to "
            "expose: " + repr(flag[:300]))


# ---------------------------------------------------------------------------
# D-086(e) -- Binding Critical 2: the certifying instant is not omissible
# ---------------------------------------------------------------------------

class TestTheCertifyingInstantIsNotOmissible(PublicationTestCase):
    """Crucible Cycle 1 Binding Critical 2, closed by the non-certifying-static
    route (D-086(e)).

    `deployment.verify(document, authority)` with no `evaluation_time` skips
    `check_lifetime` entirely and returns the payload -- the module docstring
    calls it a default the only caller "always supplies", and D-083(d) marked
    it rather than fixing it. The Crucible Adversary bound that exact code as
    a withdrawal condition; D-086 discharged the hold.

    THE RULED SEMANTICS, which these tests hold the module to: the certifying
    instant is pinned ONCE at process start and is NOT omissible. A call that
    omits it is REFUSED with `DeploymentManifestError` -- a `ValueError`
    subclass (`deployment.py:74`), so every `assertRaises(ValueError)` site in
    this file survives, and so the requirement is SEMANTIC rather than a
    Python-level positional argument that would raise `TypeError` past every
    caller's refusal path. It is never silently skipped.

    D-086(b) records that both figures used to justify the hold were wrong in
    the direction that made the fix look expensive: "17 call sites" measured
    20, and `TypeError` would only have been the outcome of the wrong fix. The
    twenty are now routed through `verify_manifest()`; the tests here call
    `deployment.verify` directly because the omission IS their subject.
    """

    OMISSION = r"(?i)evaluation.?time|instant|lifetime|clock|omit"

    def test_omitting_the_evaluation_time_is_refused_not_skipped(self):
        """FAILS ON BASELINE -- D-086(e), Binding Critical 2 condition 1.

        The fixture manifest is one hour old at NOW and would authenticate at
        any named instant near it. Called with no instant, the baseline
        returns the payload having judged nothing. It must instead refuse,
        with the error class every caller already catches, naming the omission
        as the reason -- not a `TypeError`, which no caller catches and which
        would report a programming error where a recipient needs a refusal."""
        with self.assertRaises(deployment.DeploymentManifestError) as caught:
            deployment.verify(sign_manifest(manifest_payload()), AUTHORITY)
        self.assertNotIsInstance(caught.exception, TypeError)
        self.assertRegex(
            str(caught.exception), self.OMISSION,
            "refused, but not for the omitted instant: " + str(caught.exception))

    def test_an_explicit_none_is_refused_the_same_way(self):
        """FAILS ON BASELINE -- D-086(e). `evaluation_time=None` spelled out is
        the same omission; a fix that makes the parameter required but keeps
        `None` as a sentinel meaning "skip the bound" has moved the fail-open,
        not closed it."""
        with self.assertRaises(deployment.DeploymentManifestError) as caught:
            deployment.verify(sign_manifest(manifest_payload()), AUTHORITY,
                              evaluation_time=None)
        self.assertRegex(str(caught.exception), self.OMISSION)

    def test_omitting_the_instant_cannot_revive_a_stale_manifest(self):
        """FAILS ON BASELINE -- D-086(e), the fail-open observed DIRECTLY, as
        Cycle 2 requires ("tests directly observe the original defects").

        A manifest two decades old is refused as stale at a named instant
        (`TestDeploymentManifestLifetime`, green since R-A018-16(b)) -- and
        authenticates on the baseline the moment the instant is left out.
        Omission is the one input that turns a stale manifest into a fresh one.
        Both halves are asserted so the test cannot pass on a fixture that was
        never stale."""
        stale = sign_manifest(manifest_payload(issuedAt=str(NOW - TWO_DECADES)))
        with self.assertRaises(deployment.DeploymentManifestError) as control:
            deployment.verify(stale, AUTHORITY, evaluation_time=NOW)
        self.assertRegex(str(control.exception), r"(?i)stale|age",
                         "control broken: the manifest was not stale at NOW")
        with self.assertRaises(deployment.DeploymentManifestError):
            deployment.verify(stale, AUTHORITY)

    def test_omitting_the_instant_cannot_revive_a_post_dated_manifest(self):
        """FAILS ON BASELINE -- D-086(e), the forward half. A manifest issued
        two decades hence is "not yet valid" at NOW and valid at no instant; on
        the baseline it authenticates with the instant omitted."""
        future = sign_manifest(manifest_payload(issuedAt=str(NOW + TWO_DECADES)))
        with self.assertRaises(deployment.DeploymentManifestError) as control:
            deployment.verify(future, AUTHORITY, evaluation_time=NOW)
        self.assertRegex(str(control.exception), r"(?i)future|not yet",
                         "control broken: the manifest was not post-dated at NOW")
        with self.assertRaises(deployment.DeploymentManifestError):
            deployment.verify(future, AUTHORITY)

    def test_the_refusal_class_is_a_value_error(self):
        """PASSES on baseline -- a fact about `deployment.py:74`, recorded as
        executable evidence because D-086(b)'s correction of D-083(d) rests on
        it: every `assertRaises((ValueError, KeyError))` in this file survives
        a semantic refusal precisely because of this subclassing."""
        self.assertTrue(issubclass(deployment.DeploymentManifestError, ValueError))

    def test_a_named_instant_still_authenticates(self):
        """PASSES on baseline. The control: the fix must make the instant
        non-omissible, not impossible to supply."""
        self.assertEqual(
            verify_manifest(sign_manifest(manifest_payload()))["vault"], VAULT)

    def test_the_publication_verifier_supplies_one_instant_on_both_paths(self):
        """PASSES on baseline, held so it cannot regress. `verify_publication`
        passes `evaluation_time=now` to `deployment.verify` on the certifying
        path and on the diagnostic path, and the instant it passes is the one
        it reports -- ONE instant per run, which is the observable shadow of
        "pinned once at process start". A refactor that let the only caller
        omit the instant would reopen Binding Critical 2 through the front
        door, so the caller is spied on rather than trusted."""
        cases = (
            ("certifying default clock", self.live_bundle(), None),
            ("non-certifying injected clock", self.bundle(), NOW),
        )
        for label, bundle, injected in cases:
            with self.subTest(path=label):
                with mock.patch.object(deployment, "verify",
                                       wraps=deployment.verify) as spy:
                    result = verify_publication.verify(
                        bundle.dir, bundle.manifest_file(), AUTHORITY,
                        evaluation_time=injected)
                self.assertEqual(spy.call_count, 1)
                args, kwargs = spy.call_args
                supplied = kwargs.get("evaluation_time",
                                      args[2] if len(args) > 2 else None)
                self.assertIsNotNone(
                    supplied, "the publication verifier omitted the instant")
                self.assertEqual(
                    str(supplied), result["evaluationTime"],
                    "the manifest was judged at one instant and the result "
                    "reports another")


# ---------------------------------------------------------------------------
# D-086(e) -- what the static result must disclaim
# ---------------------------------------------------------------------------

class TestTheStaticResultDisclaimsWhatItDidNotAuthenticate(PublicationTestCase):
    """D-086(e), the second sentence of the ruling: *"The static result
    explicitly disclaims deployment identity, nonce freshness, currentness and
    executability."* Four disclaimers, each asserted on the certifying path,
    where the result is a claim capable of overstating.

    Two of the four are already on the baseline's NOT_ESTABLISHED list (live
    code identity, nonce freshness). Two are not: the word "current" occurs
    nowhere on it, and "executability" occurs only inside `evaluationTimeSource`
    -- a field about the clock -- so a reader scanning the list the tool prints
    beside every result for what it did NOT establish is not told that the
    action's executability is among those things.
    """

    DISCLAIMERS = (
        ("deployment identity",
         r"(?i)deployment identity|code identity|deployed (byte)?code|what is deployed"),
        # Not a bare `nonce`: a mutation that blanked the entry's title left
        # its body, which mentions the nonce, and the clause stayed satisfied.
        ("nonce freshness", r"(?i)nonce.{0,80}(fresh|unspent|consumed)|fresh\w*.{0,40}nonce"),
        ("currentness", r"(?i)\bcurren(t|cy|tness)\b"),
        ("executability", r"(?i)executab"),
    )

    def test_the_certifying_result_disclaims_all_four(self):
        """FAILS ON BASELINE -- D-086(e). Asserted on `notEstablished` in the
        result payload, not on the whole of stdout, because stdout contains the
        payload and a match anywhere would let one field carry another's
        disclaimer. Two of the four subtests pass on the baseline; they are
        kept here rather than split off so the ruling's sentence is one test."""
        completed, headline, payload = self.certifying_run()
        # Collected, not `subTest`: see `assert_not_presented_as_a_fact`.
        missing = [name for name, pattern in self.DISCLAIMERS
                   if not any(re.search(pattern, item)
                              for item in payload["notEstablished"])]
        self.assertEqual(
            missing, [],
            "the static result does not disclaim {}: {!r}".format(
                missing, payload["notEstablished"]))

    def test_the_disclaimer_is_printed_beside_the_result_not_only_inside_it(self):
        """FAILS ON BASELINE -- D-086(e). The human-readable NOT ESTABLISHED
        line -- the one a recipient reads without parsing JSON -- must carry
        the same four. The baseline line carries two."""
        completed, headline, payload = self.certifying_run()
        printed = [line for line in completed.stdout.splitlines()
                   if line.startswith("NOT ESTABLISHED")]
        self.assertEqual(len(printed), 1, completed.stdout)
        missing = [name for name, pattern in self.DISCLAIMERS
                   if not re.search(pattern, printed[0])]
        self.assertEqual(
            missing, [],
            "the printed NOT ESTABLISHED line does not disclaim {}: {!r}".format(
                missing, printed[0]))

    def test_injected_time_is_only_available_in_the_non_certifying_mode(self):
        """PASSES on baseline, held so it cannot regress. D-086(e): injected
        time is permitted only in an explicitly non-certifying mode. The
        CLI-level witnesses are in `TestClockIsNotTheCallers`; this is the
        module-level one, so the property does not depend on `main()`'s
        exit-code mapping alone."""
        result = self._predicate(self.bundle())
        self.assertEqual(result["mode"], verify_publication.MODE_DIAGNOSTIC)
        self.assertNotEqual(result["mode"], verify_publication.MODE_STATIC)
        self.assertRegex(
            result["evaluationTimeSource"], r"(?i)non-certifying|certif\w* nothing",
            "an injected-clock result does not say it certifies nothing: "
            + repr(result["evaluationTimeSource"]))


# ---------------------------------------------------------------------------
# D-087(a) -- operation == CALL, unconditionally
# ---------------------------------------------------------------------------

class TestOperationIsCallUnconditionally(PublicationTestCase):
    """D-087(a); `docs/check-inventory-diff-2026-08-31.md` §2 row 1 and §3
    scenario 8 -- the A-and-B-versus-C axis no round had named.

    `SentinelVault.sol:357`:

        if (action.operation != uint8(T.Operation.CALL)) revert UnsupportedOperation();

    Unconditionally. `SentinelTypes.Operation` numbers DELEGATECALL 1 and
    CREATE 2 and comments both "unsupported, never executes"; there is no
    policy field that can enable them. The verifier compares `action.operation`
    to `policy["allowedOperation"]` instead, so a policy that says 1 and an
    action that says 1 agree with each other, certify, and revert on chain.
    Every bundle here is internally perfect and the policy PERMITS the
    operation; the only thing wrong is that the Vault does not.
    """

    def bundle_with_operation(self, value):
        bundle = self.bundle(seal=False)
        bundle.policy["allowedOperation"] = value
        bundle.action["operation"] = value
        return bundle.seal()

    def assert_unsupported(self, value):
        message = self.assert_refused(self.bundle_with_operation(value),
                                      r"UnsupportedOperation")
        self.assertRegex(
            message, r"\bCALL\b",
            "the refusal names the Vault error but not the one operation the "
            "Vault supports: " + message)
        self.assertNotRegex(
            message, r"(?i)not the policy's allowedOperation",
            "the policy AGREED with the action; a refusal that blames the "
            "policy sends the reader to fix the one thing that was fine "
            "(R-A018-16(c)): " + message)
        return message

    def test_delegatecall_is_refused_even_when_the_policy_allows_it(self):
        """FAILS ON BASELINE -- D-087(a). Operation 1, policy 1: certifies."""
        self.assert_unsupported("1")

    def test_create_is_refused_even_when_the_policy_allows_it(self):
        """FAILS ON BASELINE -- D-087(a). Operation 2, policy 2: certifies."""
        self.assert_unsupported("2")

    def test_an_operation_outside_the_enum_is_refused_even_when_the_policy_allows_it(self):
        """FAILS ON BASELINE -- D-087(a). 200 is a valid uint8 and no
        `Operation` member at all; the Vault's `!= CALL` refuses it without
        needing to name it, and so must this."""
        self.assert_unsupported("200")

    def test_the_policy_mismatch_refusal_is_kept(self):
        """PASSES on baseline. `TestExactActionIsEnforced.test_an_operation_
        the_policy_does_not_allow_is_refused` (operation 1, policy 0) must go on
        passing after the unconditional check lands, and it will, because its
        regex is `operation`; this test pins the sharper fact that a policy
        DISAGREEING is still refused when the operation is also not CALL, so
        the new check cannot be implemented by deleting the old one."""
        bundle = self.bundle(seal=False)
        self.assertEqual(bundle.policy["allowedOperation"], "0")
        bundle.action["operation"] = "1"
        bundle.seal()
        self.assert_refused(bundle, r"(?i)operation")

    def test_call_still_certifies(self):
        """PASSES on baseline. The control: a bundle staged through the same
        helper with operation 0 certifies, so the three refusals above are
        about the value and not about the helper."""
        self.assert_certifies(self.bundle_with_operation("0"))


# ---------------------------------------------------------------------------
# D-087(d) -- a §5.5.1 refusal record is recognised, and refused honestly
# ---------------------------------------------------------------------------

class TestARefusalRecordIsRecognisedAndNotCertified(PublicationTestCase):
    """D-087(d): *"detect a §5.5.1 bundle and refuse it with a message naming
    what it is and that this verifier does not certify refusals."* Recognise
    and refuse honestly; DO NOT VERIFY. The 32-check port was rejected by
    ruling, so nothing here asserts a refusal record's digest, signature,
    charset or bindings -- a test that did would be legislating the port.

    The shape, from `fixtures/samples/refusal-vault-paused/receipt.json` and
    `verify.py::_locate_refusal`: `receipt.json` carries `refused: true` and a
    `refusalRecord` envelope with the nine §5.5.1 fields under `record` and a
    `signature` beside them, and no `receipt` member; or the same envelope
    travels in its own `refusal.json`. On the baseline the first is refused
    with "receipt.json must carry a signed decision receipt" and the second
    with "missing required artifact receipt.json" -- both true, both the wrong
    artifact named, and neither telling the recipient that what they hold is a
    signed refusal this tool does not judge.
    """

    WRONG_ARTIFACT = (r"(?i)missing required artifact receipt\.json"
                      r"|must carry a signed decision receipt")
    NAMED = r"(?i)refusal record|SignedRefusalRecord|5\.5\.1"
    NOT_CERTIFIED = (r"(?i)(does not|cannot|will not|never|not) certif\w*"
                     r"(\s+\S+){0,3}\s+refusal|refusals? (is|are) not certif")

    def refusal_bundle(self, shape="embedded"):
        bundle = self.bundle("refusal-vault-paused", seal=False)
        self.assertIsNone(bundle.receipt, "fixture drift: the refusal bundle "
                          "now carries a receipt")
        if shape == "refusal.json":
            write_json(bundle.path("refusal.json"), bundle.receipt_doc["refusalRecord"])
            os.remove(bundle.path("receipt.json"))
        return bundle

    def assert_recognised(self, bundle):
        message = self.assert_refused(bundle, self.NAMED)
        self.assertNotRegex(
            message, self.WRONG_ARTIFACT,
            "a §5.5.1 bundle is refused for the wrong artifact: " + message)
        self.assertRegex(
            message, self.NOT_CERTIFIED,
            "the refusal names the record but does not say this verifier does "
            "not certify refusals: " + message)
        return message

    def test_the_shipped_refusal_fixture_is_refused_as_a_refusal_record(self):
        """FAILS ON BASELINE -- D-087(d). The corpus's own refusal bundle,
        untouched."""
        self.assert_recognised(self.refusal_bundle())

    def test_a_refusal_presented_in_its_own_file_is_recognised_too(self):
        """FAILS ON BASELINE -- D-087(d). `refusal.json` beside the other
        artifacts and no `receipt.json` at all: the shape the inventory diff
        staged, and the one the "missing required artifact" misdirection is
        about."""
        self.assert_recognised(self.refusal_bundle("refusal.json"))

    def test_recognition_does_not_depend_on_the_record_being_valid(self):
        """FAILS ON BASELINE -- D-087(d). Recognition is by SHAPE. A refusal
        record whose signature is garbage is still a refusal record, and the
        honest answer is still "this is a refusal and I do not certify
        refusals" -- not a signature diagnosis, which would be the first of
        the 32 checks the ruling declined to port, and not the wrong-artifact
        message either."""
        bundle = self.refusal_bundle()
        bundle.receipt_doc["refusalRecord"]["signature"] = "0x" + "00" * 65
        write_json(bundle.path("receipt.json"), bundle.receipt_doc)
        self.assert_recognised(bundle)

    def test_a_refusal_record_travelling_beside_a_receipt_does_not_certify(self):
        """FAILS ON BASELINE -- D-087(d), and the R-A018-18 shape in a new
        arm. A perfectly good ALLOW bundle with the fixture's signed refusal
        record dropped beside it in `refusal.json` certifies on the baseline
        with the file never opened. `verify.py` refuses it ("a decision OR a
        refusal, not both"). Whichever wording the refusal takes, it must name
        the refusal record: a signed refusal riding inside a PASS unread is a
        credential the run certified by omission."""
        bundle = self.bundle()
        record = read_json(SAMPLES, "refusal-vault-paused", "receipt.json")
        write_json(bundle.path("refusal.json"), record["refusalRecord"])
        self.assert_refused(bundle, self.NAMED)

    def test_a_refusal_is_refused_at_the_cli_with_the_reason_on_stderr(self):
        """FAILS ON BASELINE -- D-087(d) on the surface a recipient sees. Exit
        1, `FAIL:` on stderr naming the record and the scope, nothing on
        stdout -- the fail-closed plumbing `test_a_refusal_is_reported_on_
        stderr_with_a_nonzero_exit` already pins, carrying the new message."""
        completed = self.cli(self.refusal_bundle(),
                             extra=["--evaluation-time", str(NOW)])
        self.assertEqual(completed.returncode, 1, completed.stdout + completed.stderr)
        self.assertIn("FAIL:", completed.stderr)
        self.assertRegex(completed.stderr, self.NAMED)
        self.assertRegex(completed.stderr, self.NOT_CERTIFIED)
        self.assertNotRegex(completed.stderr, self.WRONG_ARTIFACT)
        self.assertEqual(completed.stdout, "")

    def test_a_decision_bundle_is_not_mistaken_for_a_refusal(self):
        """PASSES on baseline. The control in the other direction: the corpus
        ALLOW bundle carries `refused: false`-or-absent and no record, and
        certifies. A recogniser keyed on the wrong feature -- the `refused`
        key's presence, say -- would trip here."""
        doc = read_json(SAMPLES, "case-1-allow", "receipt.json")
        self.assertFalse(doc.get("refused"))
        self.assertNotIn("refusalRecord", doc)
        self.assert_certifies(self.bundle())


# ---------------------------------------------------------------------------
# D-087(a) -- the Vault's three §4 hard backstops are disclosed
# ---------------------------------------------------------------------------

class TestTheVaultBackstopsAreDisclosed(PublicationTestCase):
    """D-087(a); inventory diff §2 rows 2-4. `SentinelVault.sol` refuses
    `ValueOverCap` against its own immutable `maxNativeValueWei`,
    `TargetNotAllowed` against the owner-set `allowedTarget` map and
    `SelectorNotAllowed` against `allowedSelector`, AFTER the mandate's copies
    of each have passed. All three are chain state this tool cannot reach, and
    the diff classifies them OMISSION rather than N/A "because the honest
    disposition is a disclosure B does not make": NOT_ESTABLISHED names four
    things and none of them is these.

    The disclosure has to attribute each to the VAULT, because the mandate and
    policy carry a `maxNativeValueWei` of their own that IS compared, and the
    headline says so; a bare field name would read as contradicting it.
    """

    BACKSTOPS = ("maxNativeValueWei", "allowedTarget", "allowedSelector")

    def test_not_established_names_the_three_backstops_as_vault_state(self):
        """FAILS ON BASELINE -- D-087(a). In the payload and on the printed
        line, each field by name and each attributed to the Vault."""
        completed, headline, payload = self.certifying_run()
        printed = [line for line in completed.stdout.splitlines()
                   if line.startswith("NOT ESTABLISHED")]
        self.assertEqual(len(printed), 1, completed.stdout)
        # Collected, not `subTest`: see `assert_not_presented_as_a_fact`.
        unnamed, unattributed, unprinted = [], [], []
        for field in self.BACKSTOPS:
            hits = [item for item in payload["notEstablished"]
                    if re.search(re.escape(field), item)]
            if not hits:
                unnamed.append(field)
            elif not any(re.search(r"(?i)vault", item) for item in hits):
                unattributed.append(field)
            if field not in printed[0]:
                unprinted.append(field)
        self.assertEqual(
            unnamed, [],
            "notEstablished does not name the Vault's {}: {!r}".format(
                unnamed, payload["notEstablished"]))
        self.assertEqual(
            unattributed, [],
            "{} named but not attributed to the Vault, so it reads as "
            "contradicting the headline's comparison of the mandate's field of "
            "the same name: {!r}".format(unattributed, payload["notEstablished"]))
        self.assertEqual(unprinted, [],
                         "the printed NOT ESTABLISHED line omits " + repr(unprinted))


# ---------------------------------------------------------------------------
# D-087(c) -- the executability claim is stated on the surface
# ---------------------------------------------------------------------------

class TestTheExecutabilityClaimIsStated(PublicationTestCase):
    """D-087(c): the A/B split is intended and must be STATED on both
    surfaces. `verify.py` certifies AUTHENTICITY -- is this bundle genuinely
    what the signer produced -- and this tool certifies EXECUTABILITY -- would
    the Vault execute it. The split was never written down, so `=> PASS` and
    `PASS (static, offline)` were two different claims wearing one word.

    Read together with `TestTheStaticResultDisclaimsWhatItDidNotAuthenticate`,
    which requires the same run to disclaim executability AT A LIVE BLOCK: the
    claim this tool makes is the Vault's offline-checkable action predicate
    (verdict, override, windows, target, value, selector, operation), and what
    it disclaims is live state (nonce, pause, activation, code). Both have to
    be on the surface, in words that do not contradict each other, and the
    baseline has neither.
    """

    # "certifies EXECUTABILITY", "certifies static, offline executability".
    CLAIM = r"(?i)certif\w*(\s+\S+){0,4}\s+executab"
    # `verify.py` and "authenticity" in one breath, either order.
    SPLIT = (r"(?i)verify\.py(\s+\S+){0,30}\s+authentic"
             r"|authentic\w*(\s+\S+){0,30}\s+verify\.py")

    def test_the_certifying_output_states_the_claim_and_the_split(self):
        """FAILS ON BASELINE -- D-087(c). The stdout of a certifying run says
        which claim it makes and which one it does not, by name."""
        completed, headline, payload = self.certifying_run()
        text = " ".join(completed.stdout.split())
        self.assertRegex(
            text, self.CLAIM,
            "the certifying output never says this tool certifies executability")
        self.assertRegex(
            text, self.SPLIT,
            "the certifying output never says that verify.py is the tool that "
            "certifies authenticity, so the split is still unstated")

    def test_help_states_the_claim_and_the_split(self):
        """FAILS ON BASELINE -- D-087(c). `--help` reprints the module
        docstring; that docstring says "a successful run is a statement about
        STATIC AUTHENTICITY", which is A's claim wearing B's name."""
        completed = subprocess.run(
            [sys.executable, PREDICATE, "--help"], capture_output=True, text=True)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        text = " ".join(completed.stdout.split())
        self.assertRegex(text, self.CLAIM,
                         "--help never says this tool certifies executability")
        self.assertRegex(text, self.SPLIT,
                         "--help never names verify.py as the authenticity verifier")


# ---------------------------------------------------------------------------
# Coverage bookkeeping
# ---------------------------------------------------------------------------

class TestTheseModulesAreNowImported(unittest.TestCase):
    """Register §1.2's finding, turned into something that fails if it recurs.

    The 221-test suite's 15 apparent matches for "deployment" were the English
    word in comments about the legacy `domain.json` root, not the module. This
    file is the first thing in the repository to import either module."""

    def test_both_uncovered_modules_are_imported_by_this_file(self):
        self.assertIn("deployment", sys.modules)
        self.assertIn("verify_publication", sys.modules)
        self.assertEqual(
            os.path.abspath(sys.modules["deployment"].__file__),
            os.path.join(VERIFIER, "deployment.py"))
        self.assertEqual(
            os.path.abspath(sys.modules["verify_publication"].__file__),
            PREDICATE)

    def test_the_legacy_suites_deployment_matches_are_the_english_word(self):
        """Register §1.2's measurement, re-run rather than quoted.

        The 15 apparent matches for "deployment" in `test_verifier.py` are the
        English word in comments about the legacy `domain.json` root; none is an
        import of the module. Measuring it here means a reader does not have to
        take §1.2 on trust.

        NOT A TRIPWIRE. If this fails because someone added real coverage of
        these modules to `test_verifier.py`, that is a good change and this test
        is the thing that should go."""
        with open(os.path.join(VERIFIER, "test_verifier.py"), "r",
                  encoding="utf-8") as handle:
            source = handle.read()
        imports = re.findall(
            r"^\s*(?:import|from)\s+(deployment|verify_publication)\b",
            source, re.MULTILINE)
        self.assertEqual(
            imports, [],
            "test_verifier.py now imports {} -- register §1.2's coverage "
            "boundary has moved, and this bookkeeping test should be "
            "deleted".format(imports))
        self.assertGreater(source.lower().count("deployment"), 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
