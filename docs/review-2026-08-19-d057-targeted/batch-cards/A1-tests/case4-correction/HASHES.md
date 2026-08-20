# A1 case-4 correction — harness hashes

Subject file, repository-relative:
`docs/review-2026-08-19-d057-targeted/batch-cards/A1-tests/a1-repo-identity.sh`

| | sha256 | lines |
|---|---|---|
| **OLD — committed harness, unchanged** | `7be56445cc0510c03753011e21d2cea949e766a42545603289f889579145b82d` | 518 |
| **NEW — corrected harness (case 4 only)** | `54535b3b139ef9098753393872e39c932e25e0d861cfa14eb04e6f18c591122d` | 696 |

The OLD hash was verified identical in three places before any work began — the primary tree,
the pre-repair worktree and the implementation worktree — so all three started from one file:

```
shasum -a 256 docs/review-2026-08-19-d057-targeted/batch-cards/A1-tests/a1-repo-identity.sh
7be56445cc0510c03753011e21d2cea949e766a42545603289f889579145b82d   (primary tree)
7be56445cc0510c03753011e21d2cea949e766a42545603289f889579145b82d   (pre-repair worktree)
7be56445cc0510c03753011e21d2cea949e766a42545603289f889579145b82d   (implementation worktree)
```

It is also the hash `INVALIDITY-ADJUDICATION.md` records for the harness it adjudicated, so the
correction is applied to exactly the file that was adjudicated and to no other.

## The patch reproduces the NEW hash exactly

`CASE4.patch` in this directory applies to the OLD file with `patch -p1` (or `git apply`) and
yields the NEW hash:

```
patch -p1 < CASE4.patch
shasum -a 256 docs/review-2026-08-19-d057-targeted/batch-cards/A1-tests/a1-repo-identity.sh
54535b3b139ef9098753393872e39c932e25e0d861cfa14eb04e6f18c591122d
```

## Confinement, checked mechanically rather than asserted

The patch is ONE hunk, `@@ -283,18 +283,196 @@`. Removed: 9 lines, all of them case 4's own
body, its REQUIRED line and its CONTROL line. Added: 173 lines, all inside the same block.

```
lines   1-284  of OLD  ==  lines   1-284  of NEW      (byte-identical)
lines 297-518  of OLD  ==  lines 475-696  of NEW      (byte-identical, 223 elements compared)
```

Case 2 (line 232 in OLD, unchanged at line 232 in NEW) is inside the first identical region, so
it is preserved byte-for-byte, as the authorization requires. No production file was touched in
any tree.
