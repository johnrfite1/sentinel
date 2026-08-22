#!/usr/bin/env python3
"""Exact baseline oracle mutations for the corrected C-SNAPSHOT test contract."""

from __future__ import annotations

import hashlib
import sys
from collections.abc import Callable
from pathlib import Path

SUBJECT_VAULT_SHA256 = "dbff956fc2fdf6698e6c94ce4261626dc40cf219b6095ff8afcda8afcadc1185"

SUPER = '''        super(
            pendingOnly
                ? `no finalised head after ${attempts} attempts: every observation returned a ` +
                      "pending block with no hash, so there was nothing to anchor to"
                : `no stable block after ${attempts} attempts: the head moved or was replaced ` +
                      "under each pinned read",
        );'''

CHAIN_CLASS = '''export class ChainUnstableError extends Error {
    /**
     * `pendingOnly` distinguishes the two conditions this error covers (R2-F6). Every attempt
     * saw a hashless (pending) head, versus the head actually moving under the reads. Same
     * tier and same remedy, different fact — and reporting one as the other is the substitution
     * this project exists to study.
     */
    constructor(attempts: number, pendingOnly = false) {
        super(
            pendingOnly
                ? `no finalised head after ${attempts} attempts: every observation returned a ` +
                      "pending block with no hash, so there was nothing to anchor to"
                : `no stable block after ${attempts} attempts: the head moved or was replaced ` +
                      "under each pinned read",
        );
        this.name = "ChainUnstableError";
        this.pendingOnly = pendingOnly;
    }
    readonly pendingOnly: boolean = false;
}'''

EXACT_CHAIN_CLASS = '''type MutantCause = "B1" | "B2" | "B3";

function mutantExactMessage(attempts: number, causeKey: string): string {
    const messages: Readonly<Record<string, string>> = {
        B1:
            `no finalised head after ${attempts} attempts: every observation returned a ` +
            "pending block with no hash, so there was nothing to anchor to",
        B2:
            `no stable block after ${attempts} attempts: the head moved or was replaced ` +
            "under each pinned read",
        B3:
            `no finalised confirmation after ${attempts} attempts: every pinned snapshot ` +
            "was followed by a pending confirmation with no hash",
        "B1+B2":
            `no stable block after ${attempts} attempts: the run observed a pending head ` +
            "before reads and a head that moved or was replaced after pinned reads",
        "B1+B3":
            `no finalised snapshot after ${attempts} attempts: the run observed a pending ` +
            "head before reads and a pending confirmation with no hash after pinned reads",
        "B2+B3":
            `no stable snapshot after ${attempts} attempts: the run observed a head that ` +
            "moved or was replaced after pinned reads and a pending confirmation with no hash " +
            "after pinned reads",
        "B1+B2+B3":
            `no stable snapshot after ${attempts} attempts: the run observed a pending head ` +
            "before reads, a head that moved or was replaced after pinned reads, and a pending " +
            "confirmation with no hash after pinned reads",
    };
    return messages[causeKey] ?? `invalid cause set after ${attempts} attempts: ${causeKey}`;
}

export class ChainUnstableError extends Error {
    constructor(attempts: number, pendingOnly = false, causeKey?: string) {
        super(mutantExactMessage(attempts, causeKey ?? (pendingOnly ? "B1" : "B2")));
        this.name = "ChainUnstableError";
        this.pendingOnly = pendingOnly;
    }
    readonly pendingOnly: boolean = false;
}'''

INIT = '''            // Tracks whether EVERY attempt failed for the pending-head reason (R2-F6).
            let pendingOnly = true;'''

B1_END = '''                    // final; there is nothing here to attest against. `pendingOnly` stays true.
                    continue;'''

B3_END = '''                    // in; found by the D-057(5) verifier after the first repair.
                    continue;'''

B2_END = '''                    // The head genuinely moved or was replaced: condition (a).
                    pendingOnly = false;
                    continue;'''

THROW = '''            throw new ChainUnstableError(SNAPSHOT_ATTEMPTS, pendingOnly);'''


def replace_once(source: str, old: str, new: str, mutation_id: str) -> str:
    count = source.count(old)
    if count != 1:
        raise ValueError(f"mutation anchor count for {mutation_id}: {count}")
    return source.replace(old, new)


def one_replacement(old: str, new: str) -> Callable[[str, str], str]:
    return lambda source, mutation_id: replace_once(source, old, new, mutation_id)


def accumulator_mutation(source: str, mutation_id: str, recorder: str) -> str:
    source = replace_once(source, CHAIN_CLASS, EXACT_CHAIN_CLASS, mutation_id)
    source = replace_once(
        source,
        INIT,
        '''            // Mutant-only classification accumulator used to calibrate the frozen oracle.
            let pendingOnly = true;
            const causes = new Set<MutantCause>();
''' + recorder,
        mutation_id,
    )
    source = replace_once(
        source,
        B1_END,
        '''                    // final; there is nothing here to attest against. `pendingOnly` stays true.
                    recordCause("B1");
                    continue;''',
        mutation_id,
    )
    source = replace_once(
        source,
        '''                const at = head.number;''',
        '''                pendingOnly = false;
                const at = head.number;''',
        mutation_id,
    )
    source = replace_once(
        source,
        B3_END,
        '''                    // in; found by the D-057(5) verifier after the first repair.
                    recordCause("B3");
                    continue;''',
        mutation_id,
    )
    source = replace_once(
        source,
        B2_END,
        '''                    // The head genuinely moved or was replaced: condition (a).
                    recordCause("B2");
                    continue;''',
        mutation_id,
    )
    source = replace_once(
        source,
        THROW,
        '''            const causeKey = (["B1", "B2", "B3"] as const)
                .filter((cause) => causes.has(cause))
                .join("+");
            throw new ChainUnstableError(SNAPSHOT_ATTEMPTS, pendingOnly, causeKey);''',
        mutation_id,
    )
    return source


def rank_order_accumulator(source: str, mutation_id: str) -> str:
    return accumulator_mutation(
        source,
        mutation_id,
        '''            const ranks: Readonly<Record<MutantCause, number>> = {B1: 1, B2: 2, B3: 3};
            let highestRank = 0;
            const recordCause = (cause: MutantCause): void => {
                const rank = ranks[cause];
                if (rank >= highestRank) {
                    causes.add(cause);
                    highestRank = rank;
                }
            };''',
    )


def reset_on_repeat_accumulator(source: str, mutation_id: str) -> str:
    return accumulator_mutation(
        source,
        mutation_id,
        '''            const recordCause = (cause: MutantCause): void => {
                if (causes.has(cause) && causes.size > 1) causes.clear();
                causes.add(cause);
            };''',
    )


def exact_accumulator_control(source: str, mutation_id: str) -> str:
    return accumulator_mutation(
        source,
        mutation_id,
        '''            const recordCause = (cause: MutantCause): void => {
                causes.add(cause);
            };''',
    )


def freeze_after_first_repeat(source: str, mutation_id: str) -> str:
    return accumulator_mutation(
        source,
        mutation_id,
        '''            let frozen = false;
            const recordCause = (cause: MutantCause): void => {
                if (frozen) return;
                if (causes.has(cause)) {
                    frozen = true;
                    return;
                }
                causes.add(cause);
            };''',
    )


MUTATIONS: dict[str, Callable[[str, str], str]] = {
    "path_b1_as_movement": one_replacement(
        B1_END,
        '''                    // final; there is nothing here to attest against. `pendingOnly` stays true.
                    pendingOnly = false;
                    continue;''',
    ),
    "path_b2_as_pending": one_replacement(
        B2_END,
        '''                    // The head genuinely moved or was replaced: condition (a).
                    pendingOnly = true;
                    continue;''',
    ),
    "path_b3_as_movement": one_replacement(
        B3_END,
        '''                    // in; found by the D-057(5) verifier after the first repair.
                    pendingOnly = false;
                    continue;''',
    ),
    "message_swap_pure_causes": one_replacement(
        SUPER,
        '''        super(
            pendingOnly
                ? `no stable block after ${attempts} attempts: the head moved or was replaced ` +
                      "under each pinned read"
                : `no finalised head after ${attempts} attempts: every observation returned a ` +
                      "pending block with no hash, so there was nothing to anchor to",
        );''',
    ),
    "message_collapse_generic": one_replacement(
        SUPER,
        '''        super(`no stable block after ${attempts} attempts: snapshot retries exhausted`);''',
    ),
    "message_negates_pending": one_replacement(
        SUPER,
        '''        super(
            pendingOnly
                ? `no finalised head after ${attempts} attempts: no pending block with no hash ` +
                      "was observed"
                : `no stable block after ${attempts} attempts: the head moved or was replaced ` +
                      "under each pinned read",
        );''',
    ),
    "accumulator_exact_control": exact_accumulator_control,
    "accumulator_rank_order": rank_order_accumulator,
    "accumulator_reset_on_repeat": reset_on_repeat_accumulator,
    "accumulator_freeze_after_first_repeat": freeze_after_first_repeat,
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
    try:
        mutated = MUTATIONS[mutation_id](original, mutation_id)
    except ValueError as error:
        print(str(error), file=sys.stderr)
        return 2
    if mutated == original:
        print(f"dead mutation: {mutation_id}", file=sys.stderr)
        return 2
    source.write_text(mutated)
    print(mutation_id)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
