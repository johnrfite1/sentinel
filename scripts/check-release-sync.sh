#!/usr/bin/env bash
# Sentinel — release/ freshness guard (R-A018-22).
#
# WHY. `release/verifier/` shipped the PRE-REPAIR verifier while `release/MANIFEST.sha256`
# matched it perfectly: internally consistent, self-verifying, and wrong. A recipient would
# have received a verifier that certifies the corpus's real prompt-injection BLOCK bundle,
# beside a README advertising the repairs. The cause was mundane and will recur — the
# assembler was re-run mid-batch, before the verifier repairs landed, and nothing re-ran it
# afterwards. Nothing anywhere would have noticed: `grep -n "release\|assemble" scripts/test.sh
# .githooks/pre-commit` returned NOTHING. The release tree was a build artifact with no
# freshness check, in a project whose entire discipline is mechanically-enforced guards.
#
# WHAT THIS CHECKS, in two independent passes:
#
#   1. MANIFEST INTEGRITY — every row well-formed, no duplicate path, no path escaping the
#      tree, no symlink, every listed file present with a matching digest, and every released
#      file listed. This is what a recipient can run. It was already true of the defective
#      tree, which is exactly why it is not sufficient on its own and why pass 2 exists.
#
#   2. SOURCE FRESHNESS — `release/` is compared byte-for-byte against what
#      `scripts/assemble-enforcement-release.py` would produce RIGHT NOW from maintained
#      source. This is the pass the defect needed. The assembler is idempotent, so a second
#      run yields a byte-identical MANIFEST.sha256; the difference between the two trees is
#      therefore signal, never noise.
#
# THIS GUARD DOES NOT WRITE TO `release/`. A guard with a side effect on the thing it guards
# is worse than no guard: it would launder staleness into freshness on the very run that was
# supposed to report it, and it would collide with whoever is mid-edit on the assembler.
# The fresh tree is assembled into a temporary directory that is deleted afterwards. Three
# things enforce that, because one of them being wrong is how this class of accident happens:
#
#   * the assembler's output constant is REDIRECTED before `assemble()` is called, and the
#     redirection target is asserted to be inside the temporary directory;
#   * the constant is first asserted to still point at `release/` — if the assembler has been
#     restructured so that redirecting `OUT` no longer controls where it writes, this guard
#     REFUSES (exit 2) rather than running blind;
#   * `release/` is digested before and after, and a difference is a hard refusal naming this
#     script as the mutator.
#
# EXIT STATUS. 0 clean · 1 findings · 2 refused / could not check. **Exit 2 is never a pass.**
# A missing Foundry artifact, a missing assembler, or an assembler that will not run means
# this guard did not establish freshness, and it says so rather than reporting the property
# it did not check (AGENTS.md, "Mechanically Enforced Project Rules").
#
# KNOWN BOUND, stated rather than left to be discovered. This compares the release tree to
# what the assembler produces from the CURRENT working tree, including uncommitted edits and
# untracked build artifacts (`contracts/out/`). It answers "does `release/` match source?" and
# not "was `release/` built from the commit it will be published at" — that is R-A018-07's
# candidate-commit binding, which is a different item and is not closed here.

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
# Scrubbing only the identity probe left every later `git` inheriting the caller's
# environment: GIT_DIR alone made this guard report clean over a live credential, and made
# install-hooks write into a victim repository. GIT_PREFIX is included although inert on
# git 2.50.1 — an inert variable today is not a guarantee tomorrow.
unset GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE GIT_COMMON_DIR GIT_PREFIX

if ! command -v python3 >/dev/null 2>&1; then
    echo "  FAIL  python3 not found; release-sync guard refuses." >&2
    exit 2
fi

python3 - "$ROOT" <<'PY'
import hashlib
import importlib.util
import re
import sys
import tempfile
from pathlib import Path

ROOT = Path(sys.argv[1]).resolve()
RELEASE = ROOT / "release"
ASSEMBLER = ROOT / "scripts" / "assemble-enforcement-release.py"
MANIFEST_NAME = "MANIFEST.sha256"
SHOW = 20            # per-category cap on listed differences; totals are always exact.

findings = []
notes = []
counted = 0          # individual items, not category headers — a header saying "(2)" over
                     # two paths is two findings, and reporting it as one understates.


def refuse(reason, *detail):
    print(f"  FAIL  release sync: {reason}", file=sys.stderr)
    for line in detail:
        print(f"        {line}", file=sys.stderr)
    print("  This guard did not establish that release/ matches source. Exit 2 is not a pass.",
          file=sys.stderr)
    raise SystemExit(2)


def digest(path):
    h = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def snapshot(root):
    """relpath -> sha256 for every regular file under `root`. Symlinks are recorded
    separately: `is_file()` follows them, so a symlinked tree would otherwise be
    digested as though it were content."""
    files, links = {}, []
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            links.append(path.relative_to(root).as_posix())
            continue
        if path.is_file():
            files[path.relative_to(root).as_posix()] = digest(path)
    return files, links


def finding(text):
    """One standalone finding, counted like any listed item."""
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


# --- preconditions. Every one of these is a refusal, never a finding, because none of
# --- them tells you anything about whether release/ is fresh.
if not RELEASE.is_dir():
    refuse("release/ does not exist",
           "Nothing to compare. Assemble it, or remove this guard from the gate deliberately.")
if not ASSEMBLER.is_file():
    refuse(f"{ASSEMBLER.relative_to(ROOT)} is missing",
           "Freshness is defined by the assembler; without it there is no definition.")

before, before_links = snapshot(RELEASE)

# --- pass 1: manifest integrity ------------------------------------------------------
manifest_path = RELEASE / MANIFEST_NAME
if not manifest_path.is_file():
    finding(f"{MANIFEST_NAME} is missing from release/")
    listed = {}
else:
    listed = {}
    row = re.compile(r"^([0-9a-f]{64})  (.+)$")
    malformed, duplicates, escaping = [], [], []
    for number, line in enumerate(manifest_path.read_text().splitlines(), 1):
        if not line.strip():
            malformed.append(f"line {number}: blank")
            continue
        match = row.fullmatch(line)
        if not match:
            malformed.append(f"line {number}: {line[:90]!r}")
            continue
        checksum, relative = match.group(1), match.group(2)
        if relative == MANIFEST_NAME:
            finding(f"{MANIFEST_NAME} lists itself; it cannot cover its own digest")
            continue
        # A manifest row is a path a recipient's tooling will resolve. `..` or an absolute
        # path makes it resolve outside the tree the digest is supposed to be about.
        if relative.startswith("/") or ".." in Path(relative).parts:
            escaping.append(f"line {number}: {relative}")
            continue
        if relative in listed:
            duplicates.append(f"line {number}: {relative}")
            continue
        listed[relative] = checksum
    report(f"{MANIFEST_NAME}: malformed rows", malformed)
    report(f"{MANIFEST_NAME}: duplicate paths", duplicates)
    report(f"{MANIFEST_NAME}: paths escaping release/", escaping)

    present = {name for name in before if name != MANIFEST_NAME}
    report(f"{MANIFEST_NAME}: listed but absent from release/", sorted(set(listed) - present))
    report(f"{MANIFEST_NAME}: present in release/ but unlisted", sorted(present - set(listed)))
    report(
        f"{MANIFEST_NAME}: digest mismatch",
        [f"{name}: manifest {listed[name][:16]}… actual {before[name][:16]}…"
         for name in sorted(set(listed) & present) if listed[name] != before[name]],
    )

report("release/ contains symlinks (a manifest digest cannot describe a link target)",
       before_links)

# --- pass 2: source freshness --------------------------------------------------------
spec = importlib.util.spec_from_file_location("_sentinel_assembler", ASSEMBLER)
if spec is None or spec.loader is None:
    refuse("the assembler could not be loaded as a module")
assembler = importlib.util.module_from_spec(spec)
try:
    spec.loader.exec_module(assembler)
except Exception as error:                                            # noqa: BLE001
    refuse(f"importing the assembler raised {type(error).__name__}", str(error))

# THE REDIRECTION IS VALIDATED BEFORE IT IS USED. If `OUT` is not the constant that decides
# where the assembler writes, patching it would run a REAL assembly over release/ while this
# guard believed it was working in a sandbox. That is the accident this whole file exists to
# prevent, so the guard refuses instead of guessing.
declared = getattr(assembler, "OUT", None)
if not isinstance(declared, Path) or declared.resolve() != RELEASE:
    refuse("the assembler's output constant `OUT` no longer resolves to release/",
           f"OUT = {declared!r}",
           "Redirecting it can no longer be trusted to keep this guard read-only.",
           "Update this guard to match the assembler's new shape; do not run it as-is.")

with tempfile.TemporaryDirectory(prefix="sentinel-release-sync-") as sandbox:
    target = Path(sandbox).resolve() / "release"
    if not str(target).startswith(str(Path(sandbox).resolve())) or target == RELEASE:
        refuse("could not obtain a sandbox output path outside release/")
    assembler.OUT = target
    try:
        assembler.assemble()
    except SystemExit as error:
        # `assert_key_free()` raises SystemExit with its refusal text. That is a real
        # finding about source, not an inability to check, but it also means there is no
        # fresh tree to compare against, so it is reported and the run stops here.
        finding("the assembler REFUSES to produce a tree from current source:")
        for line in str(error).splitlines():
            findings.append(f"    {line}")
        fresh, fresh_links = None, []
    except FileNotFoundError as error:
        refuse("the assembler could not read one of its inputs",
               str(error),
               "Foundry artifacts under contracts/out/ are untracked; run `forge build --root",
               "contracts` and re-run. Freshness was NOT established.")
    except Exception as error:                                        # noqa: BLE001
        refuse(f"the assembler raised {type(error).__name__} on current source", str(error))
    else:
        fresh, fresh_links = snapshot(target)

    if fresh is not None:
        report("in release/ but the assembler would not produce it",
               sorted(set(before) - set(fresh)))
        report("the assembler would produce it but release/ does not have it",
               sorted(set(fresh) - set(before)))
        report("STALE — release/ differs from what the assembler would produce now",
               [name for name in sorted(set(before) & set(fresh)) if before[name] != fresh[name]])

# --- the guard proves its own innocence ----------------------------------------------
after, after_links = snapshot(RELEASE)
if after != before or after_links != before_links:
    changed = sorted(
        set(before) ^ set(after)
        | {name for name in set(before) & set(after) if before[name] != after[name]}
    )
    refuse("THIS GUARD MODIFIED release/, which it must never do",
           *(f"changed: {name}" for name in changed[:SHOW]),
           "Do not trust the result above. Restore release/ from the assembler or from git.")

for line in notes:
    print(line)

if findings:
    print()
    for line in findings:
        print(line)
    print()
    print(f"release sync: {counted} finding(s).")
    print("release/ is a BUILD ARTIFACT. Re-run scripts/assemble-enforcement-release.py to")
    print("regenerate it — do not hand-edit it, and do not weaken this guard (AGENTS.md).")
    raise SystemExit(1)

print(f"release sync: clean — {len(before)} files, MANIFEST.sha256 consistent, and the tree is")
print("byte-identical to what scripts/assemble-enforcement-release.py produces from source.")
PY
exit $?
