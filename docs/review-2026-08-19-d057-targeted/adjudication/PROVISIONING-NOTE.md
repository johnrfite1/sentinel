# Provisioning note — and an instrument defect the coordinator committed while setting up

Recorded because this project's register already carries the identical failure once (D-052) and
because the *second* half of it is the more useful finding.

## What was provisioned

Five detached worktrees at the frozen commit `c8d15a76425544148d7da2f8fa0c003feb6ad2b7`.
`ts/node_modules` is symlinked into each (a gitignored dependency tree; it takes no part in
Solidity compilation and cannot affect solc metadata). The two Foundry submodules are provisioned
as **REAL DIRECTORIES, never symlinks** — D-052 established that symlinking them makes `forge`
resolve **4** remappings instead of 5, dropping
`@openzeppelin/contracts/=lib/openzeppelin-contracts/contracts/`, which changes `settings.remappings`
in the solc metadata, the CBOR trailer, the deployed bytecode and therefore `targetCodeHash` — so
all 50 committed view digests mismatch and the deep gate cannot pass.

## The defect, committed here, in the setup itself

The first provisioning used `cp -R <src>/<lib> <dst>/<lib>` where `<dst>/<lib>` **already existed**
as the empty submodule directory `git worktree add` leaves behind. `cp -R` therefore copied the
directory *into* it, producing `contracts/lib/forge-std/forge-std/…`. **This is D-052's nesting
bug reproduced exactly** — that entry records worktrees provisioned with `ln -sfn` against
existing empty submodule directories, which nests the link instead of replacing it, and notes that
`forge build` then broke in most trees.

## The part worth recording

**The verification run immediately after provisioning did not observe the defect.** The check was
`forge remappings | wc -l`, chosen because D-052 identifies the remapping count as the signal.
It printed **5** — the correct value — against a tree whose library directories contained nothing
but a nested copy of themselves.

`forge remappings` resolves from `foundry.toml` and the *presence* of `lib/<name>`; it does not
require the library to contain any source. So the instrument was pointed at a real signal for a
real defect and was still incapable of observing this one.

This is the project's own recorded class — *an instrument can exist and point at the wrong
thing* — and it was committed by the coordinator, in the setup for a review whose subject is
that class, roughly two minutes after writing a brief warning reviewers about it.

**The corrected check is `forge build`**, which either compiles the contracts or does not, and
which failed to be run first purely because the cheaper check looked sufficient. Both worktrees
that compile Solidity (`v1`, `v3`) were re-provisioned with `cp -R <src>/<lib>/. <dst>/<lib>/` and
verified with `forge build` reporting `Compiler run successful!`.

**Bearing on the review's results:** none of the reviewer runs used the broken provisioning; the
defect was found and corrected before any reviewer was dispatched. It is recorded here rather than
discarded because a setup defect that self-reported as healthy is evidence about the method, and
discarding it would be the same omission the review exists to catch.
