#!/usr/bin/env bash
# Sentinel — release/ EXECUTION guard: the shipped verifier is run, not just digested.
#
# WHY. Three times in three days the reviewed thing and the shipped thing were different, and
# the third time every guard passed. The Cycle 2 port added `import reasoncodes` and
# `import refusal` to `verifier/verify_publication.py`; the assembler's `VERIFIER_FILES` did
# not list them; so `release/verifier/verify_publication.py` — the file a recipient actually
# runs — died on its first line of work: `ModuleNotFoundError: No module named 'reasoncodes'`.
# The release tree's own cold demo failed at its first verifier call. Meanwhile
# `check-release-sync.sh` reported clean (the tree WAS byte-identical to the assembler's
# output — the assembler was faithfully producing a broken tree) and `scripts/test.sh` reported
# GATE PASSED (it runs the SOURCE verifier, never the release copy). Nothing anywhere
# executed the shipped copy. The first two instances of this shape were caught by humans and
# reviewers, not guards; this file is the instrument that did not exist.
#
# WHAT THIS CHECKS. The tree is assembled fresh into a temporary directory — exactly as
# `check-release-sync.sh` does, never into `release/` — and the SHIPPED verifier is then run
# FROM that tree, with the working directory inside it and `PYTHONPATH` unset, so nothing can
# resolve against the repository's `verifier/`:
#
#   1. IMPORT CLOSURE — a static AST walk from the shipped `verify_publication.py`: every
#      module it imports, transitively, must be either Python standard library or a file in
#      the shipped tree. A module that is neither is named together with the file and line
#      that imports it. This is the check that would have said `reasoncodes`.
#   2. `--help` EXITS 0 from the shipped tree. The dynamic form of (1): the interpreter, not a
#      parser, resolves the imports.
#   3. SAME VERDICT AS SOURCE, on two arms. (a) CERTIFYING: the committed
#      `fixtures/samples/case-1-allow` is re-staged with every validity window moved around the
#      host clock and the whole chain re-sealed — the fixture's own receipt expired in the past
#      and the certifying path is the DEFAULT host-clock path, so a certifying run has to be
#      staged, the same way `verifier/test_publication_verifier.py::live_bundle` stages it.
#      Both copies must exit 0 with the same headline, the same CLAIM line, the same
#      `NOT ESTABLISHED` line and the same result payload. (b) FIXED-INSTANT DIAGNOSTIC: the
#      committed fixture UNTOUCHED, with `--evaluation-time` inside its receipt window. That
#      mode certifies nothing and exits 3 by design (R-A018-03), but it is fully deterministic
#      and exercises the second output arm; both copies must produce byte-identical output.
#      Each arm's deployment manifest is minted here, signed by a DERIVED authority key
#      (`keccak256("sentinel/a018 test deployment authority") mod n`, the test suite's own
#      derivation) — no private key is restated in this file.
#
# THE SOURCE RUN IS A POSITIVE CONTROL, NOT A SUBJECT. If the SOURCE verifier does not certify
# the staged bundle (arm a) or does not exit 3 on the fixed-instant arm (arm b), this guard
# REFUSES rather than comparing two failures: agreement between two crashes would establish
# nothing about the release, and a guard that goes green on that is this project's named
# failure mode. The source's own correctness is the test suite's job.
#
# THIS GUARD DOES NOT WRITE TO `release/`. Same three controls as `check-release-sync.sh`: the
# assembler's `OUT` is asserted to still resolve to `release/` before it is redirected; the
# redirection target is asserted to be inside the temporary directory; and `release/` is
# digested before and after, with any difference a hard refusal naming this script. It also
# writes no bytecode caches (`PYTHONDONTWRITEBYTECODE`), because importing the source verifier
# to mint the manifest must not leave `__pycache__` behind in `verifier/`.
#
# EXIT STATUS. 0 clean · 1 findings · 2 refused / could not check. **Exit 2 is never a pass.**
# A missing Foundry artifact, a missing assembler or fixture, an assembler that will not run,
# a source verifier that cannot be imported to mint the manifest, or a broken positive control
# means this guard did not establish that the shipped verifier executes, and it says so
# rather than reporting the property it did not check (AGENTS.md, "Mechanically Enforced
# Project Rules").
#
# KNOWN BOUNDS, printed on every run rather than left to be discovered. This runs `--help` and
# two bundles through ONE shipped file, `verifier/verify_publication.py`. It does NOT run the
# release's cold demo — `npm ci` + `forge build` + Anvil is far too heavy for the fast gate —
# so the shipped TypeScript, the shipped contracts and the demo's own verifier invocations are
# outside its reach; `release/README.md`'s cold-demo step is the only thing that exercises
# those, and it is exercised by a human. The AST walk sees `import` statements only: not
# `importlib.import_module`, `__import__`, `exec`, or data files read at runtime. It runs the
# shipped copy under THIS host's `python3`, not a recipient's.

set -uo pipefail

# --- Sentinel repository identity (D-060(2)) ---------------------------------
# Derived from THIS FILE's own location, never the caller's working directory, so a
# run from an unrelated directory or a foreign repository still inspects Sentinel.
# Every step is checked: `cd ""` returns 0 and does not abort even under `set -e`.
_sentinel_self="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd -P)" || _sentinel_self=""
if [ -z "$_sentinel_self" ]; then
    echo "  FAIL  cannot resolve this script's own location; refusing." >&2; exit 2
fi
ROOT="$(cd -- "$_sentinel_self" 2>/dev/null && env -u GIT_DIR -u GIT_WORK_TREE -u GIT_INDEX_FILE -u GIT_COMMON_DIR git rev-parse --show-toplevel 2>/dev/null)" || ROOT=""
if [ -z "$ROOT" ] || [ ! -e "$ROOT/scripts/test.sh" ] || [ ! -e "$ROOT/.githooks/pre-commit" ]; then
    echo "  FAIL  this script is not inside the Sentinel repository; refusing." >&2; exit 2
fi
cd "$ROOT" || { echo "  FAIL  cannot enter the Sentinel repository root; refusing." >&2; exit 2; }
# CALLER GIT OVERRIDES ARE REMOVED ONCE, HERE, BEFORE ANY BODY-LEVEL GIT CALL (12-F2).
unset GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE GIT_COMMON_DIR GIT_PREFIX

if ! command -v python3 >/dev/null 2>&1; then
    echo "  FAIL  python3 not found; release-execution guard refuses." >&2
    exit 2
fi

# No `__pycache__` in `verifier/` from minting, and none in the sandbox from the runs.
export PYTHONDONTWRITEBYTECODE=1

python3 - "$ROOT" <<'PY'
import ast
import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(sys.argv[1]).resolve()
RELEASE = ROOT / "release"
ASSEMBLER = ROOT / "scripts" / "assemble-enforcement-release.py"
SOURCE_VERIFIER_DIR = ROOT / "verifier"
SOURCE_VERIFIER = SOURCE_VERIFIER_DIR / "verify_publication.py"
FIXTURE = ROOT / "fixtures" / "samples" / "case-1-allow"
FOUNDRY_ARTIFACT = ROOT / "contracts" / "out" / "SentinelVault.sol" / "SentinelVault.json"
SHIPPED_ENTRY = Path("verifier") / "verify_publication.py"      # relative to the release root
# Inside the committed fixture receipt's [issuedAt, expiresAt) window — the same instant
# `verifier/test_publication_verifier.py` pins as NOW, for the same reason: fixed, so the
# diagnostic arm cannot start passing or failing as the wall clock moves.
FIXED_INSTANT = 1788059600
SHOW = 20

findings = []
counted = 0


def refuse(reason, *detail):
    print(f"  FAIL  release execution: {reason}", file=sys.stderr)
    for line in detail:
        print(f"        {line}", file=sys.stderr)
    print("  This guard did not establish that the shipped verifier executes. Exit 2 is not a pass.",
          file=sys.stderr)
    raise SystemExit(2)


def finding(text):
    global counted
    counted += 1
    findings.append(text)


def report(label, items):
    global counted
    if not items:
        return
    counted += len(items)
    findings.append(f"{label} ({len(items)})")
    for item in items[:SHOW]:
        findings.append(f"    {item}")
    if len(items) > SHOW:
        findings.append(f"    ... and {len(items) - SHOW} more")


def digest(path):
    h = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def snapshot(root):
    """relpath -> sha256 for every regular file under `root`; symlinks listed apart.
    `None` when the tree does not exist, which is a state this guard must preserve too."""
    if not root.exists():
        return None, []
    files, links = {}, []
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            links.append(path.relative_to(root).as_posix())
            continue
        if path.is_file():
            files[path.relative_to(root).as_posix()] = digest(path)
    return files, links


def clean_env():
    """The recipient's environment, not this repository's: no PYTHONPATH, no startup hooks,
    no user site. What remains is inherited so the interpreter itself still works."""
    env = {k: v for k, v in os.environ.items()
           if k not in ("PYTHONPATH", "PYTHONHOME", "PYTHONSTARTUP", "PYTHONSAFEPATH",
                        "PYTHONUSERBASE")}
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["PYTHONNOUSERSITE"] = "1"
    return env


def run_verifier(cwd, entry, argv):
    """Run `python3 <entry> argv...` with `cwd` as the working directory. `entry` is given
    RELATIVE to `cwd`, in the shape a recipient types it, so sys.path[0] is the entry's own
    directory under `cwd` and nothing else."""
    completed = subprocess.run(
        [sys.executable, str(entry)] + list(argv),
        cwd=str(cwd), env=clean_env(), capture_output=True, text=True,
    )
    return completed


# --- preconditions: refusals, never findings ------------------------------------------
if not ASSEMBLER.is_file():
    refuse(f"{ASSEMBLER.relative_to(ROOT)} is missing",
           "The shipped tree is defined by the assembler; without it there is nothing to run.")
if not SOURCE_VERIFIER.is_file():
    refuse(f"{SOURCE_VERIFIER.relative_to(ROOT)} is missing",
           "There is no source verifier to compare the shipped one against.")
if not FIXTURE.is_dir():
    refuse(f"{FIXTURE.relative_to(ROOT)} is missing",
           "The bundle both copies are run against is the committed case-1-allow fixture.")
if not FOUNDRY_ARTIFACT.is_file():
    refuse(f"{FOUNDRY_ARTIFACT.relative_to(ROOT)} is missing",
           "The assembler reads it and cannot produce a tree without it. It is untracked:",
           "run `forge build --root contracts` and re-run. Execution was NOT established.")

before, before_links = snapshot(RELEASE)

# --- load the assembler and validate the redirection BEFORE using it -----------------
spec = importlib.util.spec_from_file_location("_sentinel_assembler", ASSEMBLER)
if spec is None or spec.loader is None:
    refuse("the assembler could not be loaded as a module")
assembler = importlib.util.module_from_spec(spec)
try:
    spec.loader.exec_module(assembler)
except Exception as error:                                            # noqa: BLE001
    refuse(f"importing the assembler raised {type(error).__name__}", str(error))

declared = getattr(assembler, "OUT", None)
if not isinstance(declared, Path) or declared.resolve() != RELEASE:
    refuse("the assembler's output constant `OUT` no longer resolves to release/",
           f"OUT = {declared!r}",
           "Redirecting it can no longer be trusted to keep this guard read-only.",
           "Update this guard to match the assembler's new shape; do not run it as-is.")
if not callable(getattr(assembler, "assemble", None)):
    refuse("the assembler no longer exposes `assemble()`",
           "Update this guard to match the assembler's new shape; do not run it as-is.")

# --- mint what the runs need, from SOURCE modules -------------------------------------
# Imported from the repository's `verifier/`, not the shipped tree: the manifest and the
# re-sealed bundle are INPUTS to the comparison and must not be produced by the thing under
# test. The signing keys are the D-010 published Anvil test keys, imported from `verify.py`
# exactly as the test suite imports them, never restated (R-A018-12).
sys.path.insert(0, str(SOURCE_VERIFIER_DIR))
try:
    import deployment                                                  # noqa: E402
    import eip712                                                      # noqa: E402
    import jcs                                                         # noqa: E402
    import reasoncodes                                                 # noqa: E402
    import verify as _keys                                             # noqa: E402
    from keccak import keccak256                                       # noqa: E402
    from secp256k1 import G, N, point_mul, public_key_to_address, sign_digest  # noqa: E402
    OWNER_KEY = _keys._OWNER_TEST_KEY
    SIGNER_KEY = _keys._SENTINEL_SIGNER_TEST_KEY
except Exception as error:                                            # noqa: BLE001
    refuse(f"the SOURCE verifier modules could not be imported to mint the manifest: "
           f"{type(error).__name__}: {error}",
           "This guard compares shipped against source; it cannot run without source.")
finally:
    sys.path.pop(0)

AUTHORITY_KEY = int.from_bytes(keccak256(b"sentinel/a018 test deployment authority"), "big") % N
AUTHORITY = public_key_to_address(point_mul(AUTHORITY_KEY, G))


def read_json(path):
    with open(path, "rb") as handle:
        return json.loads(handle.read().decode("utf-8"))


def write_json(path, doc):
    with open(path, "w", encoding="ascii") as handle:
        json.dump(doc, handle)


def mint_manifest(path, mandate, receipt, issued_at):
    payload = {
        "schemaVersion": "1",
        "chainId": mandate["chainId"],
        "vault": mandate["vault"],
        "owner": mandate["principal"],
        "signer": receipt["signer"],
        "deploymentBlockNumber": "3",
        "deploymentBlockHash": "0x" + "a1" * 32,
        "runtimeCodeHash": "0x" + "b2" * 32,
        "compilerMetadataHash": "0x" + "c3" * 32,
        "sourceArchiveHash": "0x" + "d4" * 32,
        "issuedAt": str(issued_at),
    }
    digest_ = keccak256(deployment.DIGEST_TAG + jcs.canonicalize(payload))
    write_json(path, {"schema": deployment.SCHEMA, "payload": payload,
                      "authoritySignature": sign_digest(digest_, AUTHORITY_KEY)})
    return payload


def stage_live_bundle(bundle_dir, payload):
    """`fixtures/samples/case-1-allow` with every window moved around the host clock and
    the chain re-sealed: policy -> mandate -> action -> receipt, §5.6 projections re-derived,
    evidence re-hashed, mandate re-signed by the owner and receipt by the signer. Mirrors
    `test_publication_verifier.py::live_bundle` + `Bundle.seal_resynced`."""
    live = int(time.time())
    mandate = read_json(bundle_dir / "mandate.json")
    policy = read_json(bundle_dir / "policy.json")
    action = read_json(bundle_dir / "action.json")
    receipt_doc = read_json(bundle_dir / "receipt.json")
    receipt = receipt_doc["receipt"]
    evidence = read_json(bundle_dir / "evidence.json")

    receipt["issuedAt"] = str(live - 60)
    receipt["expiresAt"] = str(live + 3600)
    mandate["validAfter"] = str(live - 3600)
    mandate["validUntil"] = str(live + 7200)
    policy["validAfter"] = str(live - 3600)
    policy["validUntil"] = str(live + 7200)
    action["deadline"] = str(live + 7200)

    domain = {"name": "Sentinel", "version": "0.3",
              "chainId": payload["chainId"], "verifyingContract": payload["vault"]}

    def seal_chain():
        policy_hash = "0x" + eip712.policy_hash(policy).hex()
        mandate["policyHash"] = policy_hash
        mandate_hash = "0x" + eip712.mandate_hash(mandate).hex()
        action["policyHash"] = policy_hash
        action["mandateHash"] = mandate_hash
        action["dataHash"] = "0x" + keccak256(eip712.hex_to_bytes(action["callData"])).hex()
        receipt["policyHash"] = policy_hash
        receipt["mandateHash"] = mandate_hash
        receipt["actionHash"] = "0x" + eip712.action_hash(action).hex()
        write_json(bundle_dir / "mandate.json", mandate)
        write_json(bundle_dir / "policy.json", policy)
        write_json(bundle_dir / "action.json", action)
        receipt_doc["receipt"] = receipt
        receipt_doc["signature"] = sign_digest(eip712.receipt_digest(domain, receipt), SIGNER_KEY)
        write_json(bundle_dir / "receipt.json", receipt_doc)
        write_json(bundle_dir / "mandate-signature.json", {
            "ownerAddress": public_key_to_address(point_mul(OWNER_KEY, G)),
            "ownerSignature": sign_digest(eip712.mandate_digest(domain, mandate), OWNER_KEY),
        })

    seal_chain()                                   # final hashes for the projections
    normalized = {name: action[name] for _, name in eip712.ACTION_FIELDS}
    normalized["callData"] = action["callData"]
    evidence["normalizedAction"] = normalized
    effects = {name: mandate[name] for name in (
        "target", "selector", "resourceId", "beneficiary", "durationSeconds", "recurringAllowed")}
    effects["maxAllowanceIncreaseBaseUnits"] = policy["maxAllowanceIncreaseBaseUnits"]
    effects["maxNativeValueWei"] = str(min(int(mandate["maxNativeValueWei"]),
                                           int(policy["maxNativeValueWei"])))
    evidence["expectedEffects"] = effects
    evidence["anchor"] = {"blockNumber": receipt["simulationBlockNumber"],
                          "blockHash": receipt["simulationBlockHash"]}
    evidence["verdict"] = {0: "BLOCK", 1: "REVIEW", 2: "ALLOW"}[int(receipt["verdict"])]
    receipt["reasonCodesHash"] = reasoncodes.reason_codes_hash_hex(receipt_doc["reasonCodes"])
    canonical = jcs.canonicalize(evidence)
    write_json(bundle_dir / "evidence.json", evidence)
    (bundle_dir / "evidence.canonical.json").write_bytes(canonical)
    (bundle_dir / "evidence.hash").write_text("0x" + keccak256(canonical).hex(), encoding="ascii")
    receipt["evidenceHash"] = "0x" + keccak256(canonical).hex()
    seal_chain()                                   # re-signed over the final evidenceHash


# The AST walk, run in a SEPARATE interpreter under `-I` (isolated: no PYTHONPATH, no cwd,
# no user site) so "is this name resolvable as stdlib" is asked of a bare interpreter and
# not of this guard's own sys.path, which has just had the source `verifier/` on it.
CLOSURE_WALK = r'''
import ast, json, sys, sysconfig, importlib.util, os
root = sys.argv[1]; entry = sys.argv[2]
stdlib_dirs = {os.path.realpath(sysconfig.get_paths()[k]) for k in ("stdlib", "platstdlib")}
def classify(name):
    try:
        spec = importlib.util.find_spec(name)
    except (ImportError, ValueError):
        spec = None
    if spec is None:
        return "missing"
    if spec.origin in ("built-in", "frozen") or spec.origin is None and not spec.submodule_search_locations:
        return "stdlib"
    location = spec.origin or (spec.submodule_search_locations or [""])[0]
    location = os.path.realpath(location)
    if "site-packages" in location or "dist-packages" in location:
        return "external"
    return "stdlib" if any(location.startswith(d + os.sep) for d in stdlib_dirs) else "external"
seen, queue = {}, [entry]
missing, external, unparsable, relative = [], [], [], []
while queue:
    rel = queue.pop(0)
    if rel in seen: continue
    seen[rel] = True
    path = os.path.join(root, rel)
    try:
        tree = ast.parse(open(path, "rb").read(), filename=rel)
    except SyntaxError as e:
        unparsable.append(f"{rel}: {e.msg} (line {e.lineno})"); continue
    for node in ast.walk(tree):
        names = []
        if isinstance(node, ast.Import):
            names = [(a.name, 0) for a in node.names]
        elif isinstance(node, ast.ImportFrom):
            names = [(node.module or "", node.level)]
        for name, level in names:
            if level:
                relative.append(f"{rel}:{node.lineno}: relative import (level {level}) of {name!r}")
                continue
            top = name.split(".")[0]
            local = os.path.join(os.path.dirname(rel), top + ".py")
            local_pkg = os.path.join(os.path.dirname(rel), top, "__init__.py")
            if os.path.isfile(os.path.join(root, local)):
                queue.append(local); continue
            if os.path.isfile(os.path.join(root, local_pkg)):
                queue.append(local_pkg); continue
            kind = classify(top)
            if kind == "missing":
                missing.append(f"{top!r} imported at {rel}:{node.lineno} is neither stdlib nor shipped")
            elif kind == "external":
                external.append(f"{top!r} imported at {rel}:{node.lineno} resolves outside stdlib (site-packages)")
print(json.dumps({"walked": sorted(seen), "missing": sorted(set(missing)),
                  "external": sorted(set(external)), "unparsable": unparsable,
                  "relative": relative}))
'''


def compare_runs(label, source, shipped, normalise_json_fields=()):
    """Same exit status, same stderr, same stdout — except named payload fields, which for
    the host-clock arm carry the instant the run happened to observe."""
    diffs = []
    if source.returncode != shipped.returncode:
        diffs.append(f"exit status: source {source.returncode}, shipped {shipped.returncode}")

    def split(text):
        lines = text.splitlines()
        if lines:
            try:
                payload = json.loads(lines[-1])
            except ValueError:
                return lines, None
            for field in normalise_json_fields:
                payload.pop(field, None)
            return lines[:-1], payload
        return lines, None

    def window(a, b):
        """Both strings, cut to a window around the FIRST differing character, so a
        divergence at the tail of a long line is shown rather than hidden behind two
        identical-looking prefixes."""
        i = 0
        while i < min(len(a), len(b)) and a[i] == b[i]:
            i += 1
        start = max(0, i - 60)
        lead = "…" if start else ""
        return (f"{lead}{a[start:start + 160]}{'…' if len(a) > start + 160 else ''}",
                f"{lead}{b[start:start + 160]}{'…' if len(b) > start + 160 else ''}",
                i)

    s_lines, s_payload = split(source.stdout)
    r_lines, r_payload = split(shipped.stdout)
    if s_lines != r_lines:
        width = max(len(s_lines), len(r_lines))
        for i in range(width):
            a = s_lines[i] if i < len(s_lines) else "<absent>"
            b = r_lines[i] if i < len(r_lines) else "<absent>"
            if a != b:
                wa, wb, at = window(a, b)
                diffs.append(f"stdout line {i + 1} differs (first difference at column {at + 1}):")
                diffs.append(f"  source : {wa}")
                diffs.append(f"  shipped: {wb}")
                break
    if s_payload != r_payload:
        keys = sorted(set((s_payload or {}).keys()) | set((r_payload or {}).keys()))
        for key in keys:
            a = (s_payload or {}).get(key, "<absent>")
            b = (r_payload or {}).get(key, "<absent>")
            if a != b:
                wa, wb, at = window(json.dumps(a), json.dumps(b))
                diffs.append(f"result payload field {key!r} differs (first difference at offset {at}):")
                diffs.append(f"  source : {wa}")
                diffs.append(f"  shipped: {wb}")
                break
    if source.stderr != shipped.stderr:
        diffs.append("stderr differs:")
        diffs.append(f"  source : {source.stderr.strip().splitlines()[-1][:200] if source.stderr.strip() else '<empty>'}")
        diffs.append(f"  shipped: {shipped.stderr.strip().splitlines()[-1][:200] if shipped.stderr.strip() else '<empty>'}")
    if diffs:
        finding(f"DIVERGENT — {label}: the shipped verifier does not reach the source's result")
        for line in diffs:
            findings.append(f"    {line}")
    return not diffs


reach = {"closure": None, "help": None, "live": None, "fixed": None}

with tempfile.TemporaryDirectory(prefix="sentinel-release-exec-") as sandbox:
    sandbox = Path(sandbox).resolve()
    target = sandbox / "release"
    if not str(target).startswith(str(sandbox)) or target == RELEASE:
        refuse("could not obtain a sandbox output path outside release/")
    assembler.OUT = target
    try:
        assembler.assemble()
    except SystemExit as error:
        finding("the assembler REFUSES to produce a tree from current source:")
        for line in str(error).splitlines():
            findings.append(f"    {line}")
        fresh = False
    except FileNotFoundError as error:
        refuse("the assembler could not read one of its inputs", str(error),
               "Foundry artifacts under contracts/out/ are untracked; run `forge build --root",
               "contracts` and re-run. Execution was NOT established.")
    except Exception as error:                                        # noqa: BLE001
        refuse(f"the assembler raised {type(error).__name__} on current source", str(error))
    else:
        fresh = True

    if fresh and not (target / SHIPPED_ENTRY).is_file():
        finding(f"the assembler does not ship {SHIPPED_ENTRY.as_posix()}; there is nothing "
                "for a recipient to run")
        fresh = False

    if fresh:
        # --- 1. import closure (static) -----------------------------------------------
        walk = subprocess.run(
            [sys.executable, "-I", "-c", CLOSURE_WALK, str(target), SHIPPED_ENTRY.as_posix()],
            capture_output=True, text=True, env=clean_env(),
        )
        if walk.returncode != 0:
            refuse("the import-closure walk itself failed", walk.stderr.strip()[-400:])
        closure = json.loads(walk.stdout)
        report("IMPORT CLOSURE — module imported by the shipped verifier is neither stdlib "
               "nor in the shipped tree", closure["missing"])
        report("IMPORT CLOSURE — shipped verifier depends on a package outside the standard "
               "library (a recipient has no reason to have it)", closure["external"])
        report("IMPORT CLOSURE — shipped file does not parse", closure["unparsable"])
        report("IMPORT CLOSURE — relative import in a flat script tree", closure["relative"])
        reach["closure"] = closure["walked"]

        # --- 2. --help from the shipped tree ------------------------------------------
        help_run = run_verifier(target, SHIPPED_ENTRY, ["--help"])
        if help_run.returncode != 0 or "usage:" not in help_run.stdout:
            finding(f"SHIPPED `{SHIPPED_ENTRY.as_posix()} --help` exited {help_run.returncode} "
                    f"from the release tree (cwd inside the tree, PYTHONPATH unset):")
            tail = (help_run.stderr.strip() or help_run.stdout.strip()).splitlines()[-3:]
            for line in tail:
                findings.append(f"    {line[:200]}")
        reach["help"] = help_run.returncode == 0

        # --- 3. same verdict as source, two arms --------------------------------------
        work = sandbox / "work"
        # (b) fixed-instant diagnostic arm: the committed fixture, untouched.
        fixed_dir = work / "fixed"
        shutil.copytree(FIXTURE, fixed_dir / FIXTURE.name)
        fixed_mandate = read_json(fixed_dir / FIXTURE.name / "mandate.json")
        fixed_receipt = read_json(fixed_dir / FIXTURE.name / "receipt.json")["receipt"]
        mint_manifest(fixed_dir / "deployment-manifest.json", fixed_mandate, fixed_receipt,
                      FIXED_INSTANT - 3600)
        # (a) certifying arm: the same fixture re-staged around the host clock.
        live_dir = work / "live"
        shutil.copytree(FIXTURE, live_dir / FIXTURE.name)
        live_payload = mint_manifest(live_dir / "deployment-manifest.json", fixed_mandate,
                                     fixed_receipt, int(time.time()) - 60)
        try:
            stage_live_bundle(live_dir / FIXTURE.name, live_payload)
        except Exception as error:                                    # noqa: BLE001
            refuse(f"staging the live bundle raised {type(error).__name__}", str(error),
                   "The source modules' sealing API has moved; update this guard's staging.")

        arms = (
            ("certifying arm (host clock, re-staged case-1-allow)", live_dir, 0, [],
             ("evaluationTime",)),
            (f"fixed-instant diagnostic arm (committed case-1-allow, --evaluation-time "
             f"{FIXED_INSTANT})", fixed_dir, 3, ["--evaluation-time", str(FIXED_INSTANT)], ()),
        )
        for label, arm_dir, expected, extra, normalise in arms:
            argv = [str(arm_dir / FIXTURE.name),
                    "--deployment-manifest", str(arm_dir / "deployment-manifest.json"),
                    "--deployment-authority", AUTHORITY] + extra
            source_run = run_verifier(ROOT, SHIPPED_ENTRY, argv)
            if source_run.returncode != expected:
                refuse(f"POSITIVE CONTROL BROKEN — the SOURCE verifier exited "
                       f"{source_run.returncode}, expected {expected}, on the {label}",
                       *(line[:200] for line in
                         (source_run.stderr.strip() or source_run.stdout.strip()).splitlines()[-3:]),
                       "Two failures agreeing would establish nothing about the release, so",
                       "this guard does not compare them. Fix source (the test suite's job) first.")
            shipped_run = run_verifier(target, SHIPPED_ENTRY, argv)
            reach["live" if expected == 0 else "fixed"] = compare_runs(
                label, source_run, shipped_run, normalise_json_fields=normalise)

# --- the guard proves its own innocence ----------------------------------------------
after, after_links = snapshot(RELEASE)
if after != before or after_links != before_links:
    if before is None or after is None:
        changed = ["release/ existed before this run and not after"
                   if after is None else "release/ did not exist before this run and does now"]
    else:
        changed = sorted(
            set(before) ^ set(after)
            | {name for name in set(before) & set(after) if before[name] != after[name]}
        )
    refuse("THIS GUARD MODIFIED release/, which it must never do",
           *(f"changed: {name}" for name in changed[:SHOW]),
           "Do not trust the result above. Restore release/ from the assembler or from git.")

# --- reach and limits, printed on every run, pass or fail -----------------------------
walked = reach["closure"] or []
print("release execution — REACH of this run:")
print(f"  ran the SHIPPED {SHIPPED_ENTRY.as_posix()} from a freshly assembled temporary tree,")
print("  cwd inside that tree, PYTHONPATH unset, so no import could resolve to the repository's")
print(f"  verifier/. Static import closure walked {len(walked)} shipped file(s):"
      f" {', '.join(Path(p).name for p in walked) or '<none>'}.")
print("  Executed: `--help`; the certifying arm (case-1-allow re-staged at the host clock,")
print(f"  exit 0 expected on both copies); the fixed-instant diagnostic arm (committed fixture,")
print(f"  --evaluation-time {FIXED_INSTANT}, exit 3 expected on both). Each arm compares exit")
print("  status, every stdout line and the result payload against the SOURCE verifier's run.")
print("release execution — NOT CHECKED by this run:")
print("  * the release's cold demo (npm ci + forge build + Anvil): too heavy for the fast gate.")
print("    The shipped TypeScript, contracts and the demo's own verifier calls are outside this")
print("    guard's reach; release/README.md's cold-demo step is the only thing that runs them.")
print("  * dynamic imports: importlib.import_module, __import__, exec, string-named modules,")
print("    and data files opened at runtime. The AST walk sees `import` statements only.")
print("  * other bundles, the owner-override path, refusal records, BLOCK/REVIEW verdicts: one")
print("    ALLOW fixture on two arms is what is run. Behavioural coverage is the test suite's.")
print("  * a recipient's interpreter: the shipped copy ran under THIS host's python3"
      f" ({sys.version.split()[0]}).")
print("  * whether source is CORRECT: the source run is the positive control, not a subject.")

if findings:
    print()
    for line in findings:
        print(line)
    print()
    print(f"release execution: {counted} finding(s).")
    print("The tree scripts/assemble-enforcement-release.py produces does not execute the way")
    print("source does. Fix the ASSEMBLER (usually VERIFIER_FILES) or the source; never hand-edit")
    print("release/, and do not weaken this guard (AGENTS.md).")
    raise SystemExit(1)

print(f"release execution: clean — the shipped verifier's import closure ({len(walked)} files)")
print("is stdlib-or-shipped, `--help` exits 0 from the release tree, and both the certifying")
print("and the fixed-instant runs reach the source verifier's exact result.")
PY
exit $?
