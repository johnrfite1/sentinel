#!/usr/bin/env python3
"""Sentinel standalone receipt verifier (ratified deliverable D-010).

Independent reimplementation. Shares no canonicalization, hashing, or signing
code with the Sentinel evaluator: RFC 8785 in jcs.py, Keccak-f[1600] in
keccak.py, and secp256k1 recovery in secp256k1.py are all written here from the
published specifications. Zero third-party dependencies; stock Python 3.8+.

    python3 verifier/verify.py fixtures/samples/case-1-allow
    python3 verifier/verify.py --tamper fixtures/samples/case-1-allow
    python3 verifier/verify.py --all fixtures/samples

Exit status is 0 only if every check passes.
"""

import argparse
import copy
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import eip712  # noqa: E402
import jcs  # noqa: E402
from keccak import keccak256  # noqa: E402
from secp256k1 import RecoveryError, is_low_s, parse_signature, recover_address  # noqa: E402

# §5.4 lists `verdict` with no enumeration and no encoding. The receipts carry
# it numerically. Recovered from the samples against index.json/meta.json:
#   0 = BLOCK, 1 = REVIEW, 2 = ALLOW.
# See REPORT.md F-2: the spec never states this and §4.2 lists the cases in the
# opposite order, so ALLOW=0 is an equally defensible misreading.
VERDICT_NAMES = {0: "BLOCK", 1: "REVIEW", 2: "ALLOW"}

GREEN, RED, YELLOW, DIM, RESET = "\033[32m", "\033[31m", "\033[33m", "\033[2m", "\033[0m"


def _color(text, code):
    return f"{code}{text}{RESET}" if sys.stdout.isatty() else text


class Check:
    def __init__(self, name, ok, detail="", skipped=False):
        self.name = name
        self.ok = ok
        self.detail = detail
        self.skipped = skipped

    def render(self):
        if self.skipped:
            tag = _color("SKIP", YELLOW)
        else:
            tag = _color("PASS", GREEN) if self.ok else _color("FAIL", RED)
        line = f"  [{tag}] {self.name}"
        if self.detail:
            line += "\n" + "\n".join(
                "         " + _color(l, DIM) for l in self.detail.splitlines()
            )
        return line


def _read_bytes(path):
    with open(path, "rb") as handle:
        return handle.read()


def _read_json(path):
    return jcs.parse_bytes(_read_bytes(path))


def _norm_hex(value):
    return value.lower() if isinstance(value, str) else value


def _find_domain(sample_dir, override):
    if override:
        return override
    for candidate in (
        os.path.join(sample_dir, "domain.json"),
        os.path.join(os.path.dirname(os.path.abspath(sample_dir)), "domain.json"),
    ):
        if os.path.isfile(candidate):
            return candidate
    raise FileNotFoundError(
        "domain.json not found in the sample directory or its parent; "
        "pass --domain"
    )


TAMPER_MODES = ("evidence", "receipt", "signature")


def verify_sample(sample_dir, domain_path=None, tamper=None):
    """Run every check against one sample directory. Returns (ok, [Check])."""
    checks = []
    sample_dir = os.path.abspath(sample_dir)

    # ---- load -----------------------------------------------------------
    evidence_raw = _read_bytes(os.path.join(sample_dir, "evidence.json"))
    canonical_expected = _read_bytes(os.path.join(sample_dir, "evidence.canonical.json"))
    hash_expected = _read_bytes(os.path.join(sample_dir, "evidence.hash")).decode().strip()
    receipt_doc = _read_json(os.path.join(sample_dir, "receipt.json"))
    domain = _read_json(_find_domain(sample_dir, domain_path))

    evidence = jcs.parse_bytes(evidence_raw)
    if tamper == "evidence":
        evidence = _tamper_json(evidence)
    elif tamper == "receipt":
        receipt_doc = copy.deepcopy(receipt_doc)
        if receipt_doc.get("receipt"):
            # Flip the low bit of issuedAt: still a well-typed uint64, so the
            # struct still encodes -- only the digest, and so the recovered
            # address, changes.
            body = receipt_doc["receipt"]
            body["issuedAt"] = str(int(body["issuedAt"]) ^ 1)
    elif tamper == "signature":
        receipt_doc = copy.deepcopy(receipt_doc)
        if receipt_doc.get("signature"):
            sig = receipt_doc["signature"]
            flipped = "%02x" % (int(sig[2:4], 16) ^ 0x01)
            receipt_doc["signature"] = "0x" + flipped + sig[4:]
    elif tamper is not None:
        raise ValueError(f"unknown tamper mode {tamper!r}")

    # ---- 1. recanonicalize ---------------------------------------------
    canonical_actual = jcs.canonicalize(evidence)
    ok = canonical_actual == canonical_expected
    detail = ""
    if not ok:
        detail = _byte_diff(canonical_actual, canonical_expected)
    else:
        detail = f"{len(canonical_actual)} bytes, byte-identical, no trailing newline"
        if canonical_expected.endswith(b"\n"):
            detail = f"{len(canonical_actual)} bytes, byte-identical"
    checks.append(Check("RFC 8785 recanonicalization matches evidence.canonical.json", ok, detail))

    # ---- 2. keccak256 of the canonical bytes ----------------------------
    # Hash what we recomputed, not what was handed to us: hashing the supplied
    # canonical file would let a mismatch in check 1 pass unnoticed here.
    evidence_hash = "0x" + keccak256(canonical_actual).hex()
    expected_hash = _norm_hex(hash_expected)
    if not expected_hash.startswith("0x"):
        expected_hash = "0x" + expected_hash
    ok = evidence_hash == expected_hash
    checks.append(Check(
        "keccak256(canonical bytes) matches evidence.hash",
        ok,
        f"computed {evidence_hash}" + ("" if ok else f"\nfile     {expected_hash}"),
    ))

    refused = bool(receipt_doc.get("refused"))
    receipt = receipt_doc.get("receipt")
    signature = receipt_doc.get("signature")

    if refused or receipt is None or signature is None:
        reason = receipt_doc.get("refusalReason") or receipt_doc.get("reason")
        note = "signer refused to issue a receipt" if refused else "no receipt/signature present"
        if reason:
            note += f": {reason}"
        note += "\nevidence checks above still apply; receipt-bound checks are not applicable"
        checks.append(Check("receipt evidenceHash binding", True, note, skipped=True))
        checks.append(Check("EIP-712 signature recovers the declared signer", True, note, skipped=True))
        if refused and receipt is not None:
            checks.append(Check(
                "refusal shape is self-consistent",
                False,
                "refused is true but a receipt body is also present; a refusal "
                "must not carry a signed receipt",
            ))
        return all(c.ok for c in checks), checks

    # ---- 3. receipt binds the evidence ----------------------------------
    receipt_evidence_hash = _norm_hex(receipt.get("evidenceHash", ""))
    ok = receipt_evidence_hash == evidence_hash
    checks.append(Check(
        "receipt.evidenceHash binds the recomputed evidence",
        ok,
        "" if ok else f"receipt   {receipt_evidence_hash}\ncomputed  {evidence_hash}",
    ))

    # ---- 4. EIP-712 digest and signer recovery --------------------------
    try:
        separator = eip712.domain_separator(domain)
        struct_hash = eip712.receipt_struct_hash(receipt)
        digest = eip712.receipt_digest(domain, receipt)
        recovered = recover_address(digest, signature)
        recover_error = None
    except (eip712.EncodingError, RecoveryError, ValueError) as exc:
        separator = struct_hash = digest = None
        recovered = None
        recover_error = str(exc)

    if recover_error:
        checks.append(Check("EIP-712 digest recomputation", False, recover_error))
        checks.append(Check("signature recovers the declared signer", False, recover_error))
    else:
        checks.append(Check(
            "EIP-712 digest recomputed from §5.4 field list",
            True,
            f"domainSeparator 0x{separator.hex()}\n"
            f"structHash      0x{struct_hash.hex()}\n"
            f"digest          0x{digest.hex()}",
        ))

        declared = _norm_hex(receipt.get("signer", ""))
        ok = recovered == declared
        checks.append(Check(
            "recovered signer == receipt.signer",
            ok,
            f"recovered {recovered}" + ("" if ok else f"\ndeclared  {declared}"),
        ))

        domain_signer = _norm_hex(domain.get("signerAddress", ""))
        ok = recovered == domain_signer
        checks.append(Check(
            "recovered signer == domain.json signerAddress",
            ok,
            "" if ok else f"recovered {recovered}\ndomain    {domain_signer}",
        ))

        _, s_value, v_value = parse_signature(signature)
        checks.append(Check(
            "signature is EIP-2 canonical (low-s) and v in {27,28}",
            is_low_s(s_value) and v_value in (27, 28),
            f"v={v_value}, low-s={is_low_s(s_value)}",
        ))

    # ---- 5. verdict sanity ----------------------------------------------
    checks.append(_verdict_check(sample_dir, receipt))

    # ---- 6. the rest of the hash chain ----------------------------------
    checks.extend(_chain_checks(sample_dir, receipt, evidence))

    return all(c.ok for c in checks), checks


def _chain_checks(sample_dir, receipt, evidence):
    """Recompute every other hash the receipt commits to.

    §5 does not say these are EIP-712 hashStruct values; that was recovered by
    search (REPORT.md F-5). Without these, a receipt could be correctly signed
    over the *wrong* mandate and still pass every other check in this file.
    """
    out = []

    def load(name):
        path = os.path.join(sample_dir, name)
        return _read_json(path) if os.path.isfile(path) else None

    mandate, policy, action = load("mandate.json"), load("policy.json"), load("action.json")

    for doc, fn, field, label in (
        (mandate, eip712.mandate_hash, "mandateHash", "§5.1 MandatePayload"),
        (policy, eip712.policy_hash, "policyHash", "§5.2 PolicyPayload"),
        (action, eip712.action_hash, "actionHash", "§5.3 ActionPayload"),
    ):
        if doc is None:
            out.append(Check(f"recomputed {field} from {label}", True,
                             "payload file not present in this sample", skipped=True))
            continue
        try:
            computed = "0x" + fn(doc).hex()
        except eip712.EncodingError as exc:
            out.append(Check(f"recomputed {field} from {label}", False, str(exc)))
            continue
        declared = _norm_hex(receipt.get(field, ""))
        ok = computed == declared
        out.append(Check(
            f"recomputed {field} from {label} matches the receipt",
            ok,
            "" if ok else f"computed {computed}\nreceipt  {declared}",
        ))

    # calldata -> dataHash, the one place the raw call is bound.
    if action and "callData" in action:
        computed = "0x" + keccak256(bytes.fromhex(_norm_hex(action["callData"])[2:])).hex()
        ok = computed == _norm_hex(action.get("dataHash", ""))
        out.append(Check("keccak256(callData) matches action.dataHash", ok,
                         "" if ok else f"computed {computed}\naction   {action.get('dataHash')}"))

    # Cross-references that §5 lists as fields but never requires to agree.
    if mandate and policy:
        out.append(Check(
            "mandate.policyHash == receipt.policyHash",
            _norm_hex(mandate.get("policyHash", "")) == _norm_hex(receipt.get("policyHash", "")),
        ))
    if action:
        out.append(Check(
            "action binds the same mandate and policy as the receipt",
            _norm_hex(action.get("mandateHash", "")) == _norm_hex(receipt.get("mandateHash", ""))
            and _norm_hex(action.get("policyHash", "")) == _norm_hex(receipt.get("policyHash", "")),
        ))

    # Evidence-bundle fields §5.6 does not list, and never requires to agree
    # with the receipt (REPORT.md F-3). Checked anyway: if they can disagree,
    # the dashboard and the receipt can tell an operator different stories.
    anchor = evidence.get("anchor") if isinstance(evidence, dict) else None
    if isinstance(anchor, dict):
        ok = (str(anchor.get("blockNumber")) == str(receipt.get("simulationBlockNumber"))
              and _norm_hex(anchor.get("blockHash", "")) == _norm_hex(receipt.get("simulationBlockHash", "")))
        out.append(Check(
            "evidence.anchor matches the receipt's simulation block",
            ok,
            "" if ok else f"anchor  {anchor}\nreceipt {receipt.get('simulationBlockNumber')} "
                          f"{receipt.get('simulationBlockHash')}",
        ))
    if isinstance(evidence, dict) and "verdict" in evidence:
        expected = VERDICT_NAMES.get(int(receipt["verdict"]))
        ok = evidence["verdict"] == expected
        out.append(Check(
            "evidence.verdict agrees with the receipt's verdict enum",
            ok,
            "" if ok else f"evidence says {evidence['verdict']}, receipt decodes to {expected}",
        ))

    # The one binding this verifier cannot check. Stated loudly rather than
    # quietly omitted: see REPORT.md F-6.
    out.append(Check(
        "reasonCodesHash recomputed from the evidence bundle",
        True,
        "NOT VERIFIABLE: §5.4 names reasonCodesHash but never defines its "
        "preimage, so an independent party cannot recompute it. A receipt "
        "signed over the correct evidence with a substituted reason-code set "
        "would pass every other check here.",
        skipped=True,
    ))
    return out


def _verdict_check(sample_dir, receipt):
    try:
        verdict_num = int(receipt["verdict"])
    except (KeyError, TypeError, ValueError):
        return Check("verdict decodes to a known enum member", False,
                     f"verdict is {receipt.get('verdict')!r}")
    name = VERDICT_NAMES.get(verdict_num)
    if name is None:
        return Check("verdict decodes to a known enum member", False,
                     f"verdict {verdict_num} is outside 0..2")

    expected = None
    meta_path = os.path.join(sample_dir, "meta.json")
    if os.path.isfile(meta_path):
        expected = _read_json(meta_path).get("verdict")
    if expected is None:
        index_path = os.path.join(os.path.dirname(sample_dir), "index.json")
        if os.path.isfile(index_path):
            for entry in _read_json(index_path):
                if entry.get("id") == os.path.basename(sample_dir):
                    expected = entry.get("verdict")
    if expected is None:
        return Check(f"verdict {verdict_num} decodes to {name}", True,
                     "no meta.json/index.json to cross-check against", skipped=True)
    ok = expected == name
    return Check(
        f"verdict {verdict_num} decodes to {name}, matching the case label",
        ok,
        "" if ok else f"case label says {expected}, receipt decodes to {name}",
    )


def _tamper_json(evidence):
    """Mutate exactly one byte-equivalent of the evidence, in place-ish.

    A verifier that cannot fail is not a verifier. This flips a single character
    deep inside a nested string so that neither the JSON shape nor the key set
    changes -- only the canonical bytes.
    """
    mutated = copy.deepcopy(evidence)

    def walk(node):
        if isinstance(node, dict):
            for key in sorted(node):
                if walk_value(node, key):
                    return True
            return False
        if isinstance(node, list):
            for index in range(len(node)):
                if walk_value(node, index):
                    return True
        return False

    def walk_value(container, key):
        value = container[key]
        if isinstance(value, str) and value:
            last = value[-1]
            replacement = "0" if last != "0" else "1"
            container[key] = value[:-1] + replacement
            return True
        return walk(value)

    if not walk(mutated):
        raise RuntimeError("no string leaf found to tamper with")
    return mutated


def _byte_diff(actual, expected):
    limit = min(len(actual), len(expected))
    for i in range(limit):
        if actual[i] != expected[i]:
            lo, hi = max(0, i - 40), min(limit, i + 40)
            return (
                f"first difference at byte {i} "
                f"(lengths {len(actual)} vs {len(expected)})\n"
                f"computed ...{actual[lo:hi]!r}...\n"
                f"expected ...{expected[lo:hi]!r}..."
            )
    return f"one is a prefix of the other: lengths {len(actual)} vs {len(expected)}"


def run(sample_dir, domain_path=None, tamper=None, quiet=False, verbose=True):
    label = os.path.basename(os.path.abspath(sample_dir))
    try:
        ok, checks = verify_sample(sample_dir, domain_path, tamper)
    except Exception as exc:  # noqa: BLE001 - a crash is a verification failure
        if not quiet:
            print(f"{label}: {_color('ERROR', RED)} {type(exc).__name__}: {exc}")
        return False, [Check("verification ran to completion", False, str(exc))]

    if not quiet:
        suffix = f" {_color('[tamper: ' + tamper + ']', YELLOW)}" if tamper else ""
        print(f"{label}{suffix}")
        if verbose:
            for check in checks:
                print(check.render())
    if tamper:
        rejected = not ok
        if not quiet:
            outcome = _color("PASS", GREEN) if rejected else _color("FAIL", RED)
            print(f"  => tamper self-test {outcome}: "
                  f"{'correctly rejected' if rejected else 'WRONGLY ACCEPTED'} "
                  f"the mutated {tamper}\n")
        return rejected, checks

    if not quiet:
        print(f"  => {_color('PASS', GREEN) if ok else _color('FAIL', RED)}\n")
    return ok, checks


def run_tamper_suite(sample_dir, domain_path=None, quiet=False, verbose=False):
    """Every tamper mode must be rejected. Returns True only if all are."""
    results = []
    for mode in TAMPER_MODES:
        rejected, _ = run(sample_dir, domain_path, tamper=mode,
                          quiet=quiet, verbose=verbose)
        results.append(rejected)
    return all(results)


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Verify a Sentinel decision receipt end to end.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("sample", nargs="+", help="sample directory (or, with --all, its parent)")
    parser.add_argument("--domain", help="path to domain.json (default: sample dir, then parent)")
    parser.add_argument("--tamper", nargs="?", const="all", choices=("all",) + TAMPER_MODES,
                        help="self-test: mutate the artifact and require verification to FAIL "
                             "(default 'all' runs every mode)")
    parser.add_argument("--all", action="store_true",
                        help="treat each argument as a directory of sample directories")
    parser.add_argument("--print-types", action="store_true",
                        help="print the derived EIP-712 type strings and exit")
    args = parser.parse_args(argv)

    if args.print_types:
        print("domain type:", eip712.DOMAIN_TYPE)
        print("struct type:", eip712.RECEIPT_TYPE)
        return 0

    targets = []
    for path in args.sample:
        if args.all:
            targets.extend(
                os.path.join(path, entry)
                for entry in sorted(os.listdir(path))
                if os.path.isdir(os.path.join(path, entry))
            )
        else:
            targets.append(path)

    if args.tamper == "all":
        oks = [run_tamper_suite(t, args.domain, verbose=False) for t in targets]
    else:
        oks = [run(t, args.domain, args.tamper)[0] for t in targets]
    failed = [t for t, ok in zip(targets, oks) if not ok]
    passed = len(oks) - len(failed)
    print(f"{passed}/{len(oks)} sample(s) "
          f"{'rejected every tamper mode' if args.tamper else 'verified'}")
    for target in failed:
        print(f"  {_color('FAILED', RED)}: {target}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
