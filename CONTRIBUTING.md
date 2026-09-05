# Contributing

This repository is published as a demonstration of one author's engineering work, and its record
— every ruling, review and correction — is part of what is on show. It is not, at present, run as
a community project, and there is no roadmap to contribute against.

**What is welcome:** a report that a tool or a document here claims more than it establishes (see
`SECURITY.md`); a reproduction that disagrees with a measured claim in the README or the release
tree; a correction to a factual error in the docs, with the command that shows it.

**What will not be merged:** changes to the mechanism, the verifiers or the tests without a prior
conversation — every one of those is under a recorded ruling in `docs/decisions.md`, and the
project's own rule is that agents propose and the author decides. Please open an issue first.

**Before you run anything:** read `README.md` top to bottom, then `release/README.md`. The fast
gate is `./scripts/test.sh` and needs Node (see `.nvmrc`), Foundry (`forge`, `anvil`) and
Python 3.8+ with no third-party packages; it says what it did not run.

**Licence:** Apache-2.0 (`LICENSE`, `NOTICE`). By contributing you agree your contribution is
licensed the same way.
