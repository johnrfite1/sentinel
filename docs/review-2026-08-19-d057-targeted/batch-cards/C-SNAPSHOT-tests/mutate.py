#!/usr/bin/env python3
"""Exact baseline oracle mutations for the frozen C-SNAPSHOT test contract."""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

SUBJECT_VAULT_SHA256 = "dbff956fc2fdf6698e6c94ce4261626dc40cf219b6095ff8afcda8afcadc1185"

SUPER = '''        super(
            pendingOnly
                ? `no finalised head after ${attempts} attempts: every observation returned a ` +
                      "pending block with no hash, so there was nothing to anchor to"
                : `no stable block after ${attempts} attempts: the head moved or was replaced ` +
                      "under each pinned read",
        );'''

MUTATIONS: dict[str, tuple[str, str]] = {
    "path_b1_as_movement": (
        '''                    // final; there is nothing here to attest against. `pendingOnly` stays true.
                    continue;''',
        '''                    // final; there is nothing here to attest against. `pendingOnly` stays true.
                    pendingOnly = false;
                    continue;''',
    ),
    "path_b2_as_pending": (
        '''                    // The head genuinely moved or was replaced: condition (a).
                    pendingOnly = false;
                    continue;''',
        '''                    // The head genuinely moved or was replaced: condition (a).
                    pendingOnly = true;
                    continue;''',
    ),
    "path_b3_as_movement": (
        '''                    // in; found by the D-057(5) verifier after the first repair.
                    continue;''',
        '''                    // in; found by the D-057(5) verifier after the first repair.
                    pendingOnly = false;
                    continue;''',
    ),
    "message_swap_pure_causes": (
        SUPER,
        '''        super(
            pendingOnly
                ? `no stable block after ${attempts} attempts: the head moved or was replaced ` +
                      "under each pinned read"
                : `no finalised head after ${attempts} attempts: every observation returned a ` +
                      "pending block with no hash, so there was nothing to anchor to",
        );''',
    ),
    "message_collapse_generic": (
        SUPER,
        '''        super(`no stable block after ${attempts} attempts: snapshot retries exhausted`);''',
    ),
}


def main() -> int:
    if len(sys.argv) == 2 and sys.argv[1] == "--list":
        print("\n".join(MUTATIONS))
        return 0
    if len(sys.argv) != 3:
        print("usage: mutate.py <subject-checkout> <mutation-id>", file=sys.stderr)
        return 2
    root = Path(sys.argv[1]).resolve()
    mutation_id = sys.argv[2]
    if mutation_id not in MUTATIONS:
        print(f"unknown mutation: {mutation_id}", file=sys.stderr)
        return 2
    source = root / "ts/src/signer/vault.ts"
    original = source.read_text()
    digest = hashlib.sha256(original.encode()).hexdigest()
    if digest != SUBJECT_VAULT_SHA256:
        print(f"refusing non-subject vault: sha256={digest}", file=sys.stderr)
        return 2
    old, new = MUTATIONS[mutation_id]
    if original.count(old) != 1:
        print(f"mutation anchor count for {mutation_id}: {original.count(old)}", file=sys.stderr)
        return 2
    mutated = original.replace(old, new)
    if mutated == original:
        print(f"dead mutation: {mutation_id}", file=sys.stderr)
        return 2
    source.write_text(mutated)
    print(mutation_id)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
