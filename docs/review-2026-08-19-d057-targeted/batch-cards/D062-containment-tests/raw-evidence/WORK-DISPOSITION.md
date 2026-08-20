# THE VERIFIER'S SYNTHETIC WORKING REPOSITORIES — INSPECTION AND DISPOSITION

The independent D-062 verifier left two scratch areas. `out/` held **primary evidence** and is
preserved beside this file. This note records the inspection of the other one, whose contents are
**fixtures rather than measurements**, so that its removal is a recorded decision rather than a
silent one.

**Nothing from it is committed.** Committing entire synthetic repositories is expressly not the
intent; what mattered was establishing that none of it was unique.

## THE TWO DIRTY WORKING TREES, RECORDED IN FULL

Both were flagged dirty, and both turned out to be the same thing.

| | `ctl-tmp` | `ctl-tmp2` |
|---|---|---|
| HEAD | `4920213` — the committed containment repair | `74eb34d` — a local commit, **not** in this repository |
| dirty path | `zz-fixture-d062v.md` — **untracked** | `zz-fixture-d062v.md` — **modified** |
| size | 80 bytes | 80 bytes |
| tracked at that path here? | no | no |
| content | the planted synthetic fixture credential | the same |

`74eb34d` is titled *seed fixture* and its whole diff is **one file, two insertions** — that same
fixture. It carries no measurement, no probe output and no patch.

**The fixture's content is a synthetic token the harness assembles at run time from one repeated
hex character, bound to a key-shaped identifier.** It is the same token disclosed in
`SANITIZATION-MANIFEST.md`, so its exact shape is already preserved there. It is not a credential
and never was.

## THE OTHER NINETEEN ENTRIES

Twelve synthetic repositories and directories built by the harness (`BASE`, `SUBJ`, their
`-cen` / `-lay` / `-gd` / `b` variants, `atk`, `atk2`, `callerval`, `degen`, `forms`, `misc`,
`probehooks`, `vicfp`) plus two raw index files (`decoy-clean.idx`, and a zero-byte
`foreign.idx`). All are **inputs the harness constructs**, reconstructible by re-running it.

## DISPOSITION

**Uniqueness ruled out.** The only content not already present in this repository or in the
preserved `out/` evidence is the planted fixture above, which carries no result. **No measurement
and no patch was found**, so nothing was extracted.

On that basis the fixture directories are disposable, and were removed **only after** the `out/`
evidence was committed and verified — by exact literal path, with no glob, no broad parent and no
force flag. **D-063 stands: no standing force authorization exists, and none was assumed here.**
