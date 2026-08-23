# V-1 index-path ordering — coverage (D-059(7))

> *"A standalone script that nothing invokes repeats the defect this work is trying to close.
> Required: invocation by the applicable fast and deep gate paths; a TOP-LEVEL falsification
> showing THE GATE fails when the targeted fact is wrong; an unchanged control showing the real
> gate passes; and an explicit statement that the guard covers only its enumerated canonical facts
> and is NOT general prose-consistency evidence."* — D-059(7)

**Guard:** `scripts/check-v1-index-ordering.sh`
**Invocation:** `scripts/test.sh`, both profiles, in the shared prefix after the secret guard
and before the rename gate. The step is not enclosed in any `PROFILE` branch; the first
profile-dependent statement remains the Foundry step. A deep mutation rerun is therefore not
required unless that control flow moves.

## Enumerated facts (the whole of what a pass means)

1. **CS.** `scripts/check-secrets.sh --staged --index-file <hostile>` with `GIT_INDEX_FILE`
   exported to that same hostile path, while credential-shaped content sits in the real staged
   index, refuses at validation and names the canonical index directory. It does not print
   `secret guard: clean`.
2. **HOOK.** `.githooks/pre-commit` invoked by a real `git commit` with `GIT_INDEX_FILE`
   exported to a hostile path outside the canonical index directory blocks the commit: non-zero
   exit, HEAD unmoved, the hook's own validation wording.

## Controls that keep the probe live

- Applying the reverse-ordering mutant to a **copy** of `check-secrets.sh` makes the same CS
  invocation accept and print `secret guard: clean`. If that does not happen, the instrument
  exits 2 and no REQUIRED verdict may be read.
- Applying the same mutant to a **copy** of `pre-commit` shifts the refusal from the hook's
  own wording to `check-secrets.sh`'s `--index-file` refusal; HEAD stays unmoved.

## Explicitly not covered

This guard is **not** general evidence about index-handling of any other file, about
`GIT_DIR` / `GIT_WORK_TREE`, about untracked-file hygiene (V-6), about staged rename or
typechange (R1), or about a hook-path commit being *accepted* after the hook's directory check
is reversed. That last end-to-end was not constructed: the hook unsets `GIT_INDEX_FILE` before
`exec`, and `check-secrets.sh` re-validates independently. Naming that limit is the coverage
statement D-059(7) requires, not a residual to repair here.

A source-text order check is not offered and must not be substituted.
