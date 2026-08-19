# LENS 2 — `ts/src/signer/**` + the Solidity type mirror. DIRECTED.

**Your assignment, stated as a goal rather than a topic: OBTAIN A SIGNED ALLOW THAT THE
DESIGN FORBIDS.** That is the exact shape of this project's only CRITICAL (A-043): a
signed ALLOW obtainable for calldata nobody decoded, reproduced twice onchain.

**Your surface:** the isolated signer process, its request handling, its attestation path,
the EIP-712 typed-data construction, and the Solidity type-string mirror that must agree
with it byte for byte.

**The specific lead you are handed:** `Object.hasOwn` replaced `in` at the verdict boundary
as a repair (the `verdict in VERDICT` prototype-chain defect, E1). **A repair that closes
the branch its reviewer exploited and leaves the identical hole two lines down is this
project's signature failure.** Find the sibling. Look for every other place a
caller-controlled string indexes an object, walks a prototype chain, or is tested for
membership by a different idiom than the repaired one.

**Other angles, unconfirmed:**
- The signer must not be able to mint the owner's credential (§3.3(7)). Probe it directly.
- Anything the signer attests but does not check. `E3` (anchor recency) is a RECORDED,
  OPEN design fork held by John — **do not re-report it, and do not "fix" it** — but if you
  can show it is WORSE than recorded, that IS a new finding.
- Two wire integer fields escaping `bounded()` is recorded as `E2`. Same rule applies.
- The type mirror: can the TS and Solidity sides be made to disagree without any test
  failing? The type-string guard is one of the ten stages — is it complete?

**Falsify properly:** to test a check, make the request or bundle wholly self-consistent so
only the check under test can reject it. A rejection that comes from a different check
tells you nothing.

`export PATH="$HOME/.foundry/bin:$PATH"`. Baseline first, on the untouched worktree.
