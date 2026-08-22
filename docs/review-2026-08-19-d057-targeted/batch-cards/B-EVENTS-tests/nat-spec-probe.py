#!/usr/bin/env python3
"""Fail unless SentinelVault carries the exact frozen truthful F7-R1 replacement."""

from pathlib import Path
import sys


FALSE_CLAIM = """        // §3.3(2)'s "logged", emitted AFTER authentication and BEFORE the call — so the log
        // records only authorizations that actually passed, and records them even if the
        // external call then reverts the transaction away. (D-043)
"""

TRUTHFUL_REPLACEMENT = """        // §3.3(2)'s "logged": emitted after every override-authentication check passes and
        // before the external call. A durable OverrideAuthorized log exists only if the
        // downstream call succeeds and every enclosing call frame commits. Any revert of
        // this frame or an ancestor discards the log and nonce update. The event therefore
        // records an override authorization consumed by a successful, retained vault
        // execution; it does not record a failed or merely attempted override. (D-043, F7-R1)
"""


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("usage: nat-spec-probe.py CHECKOUT")
    source = Path(sys.argv[1]).resolve() / "contracts/src/SentinelVault.sol"
    text = source.read_text()
    false_count = text.count(FALSE_CLAIM)
    truthful_count = text.count(TRUTHFUL_REPLACEMENT)
    print(f"false_claim_count={false_count}")
    print(f"truthful_replacement_count={truthful_count}")
    if false_count != 0 or truthful_count != 1:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
