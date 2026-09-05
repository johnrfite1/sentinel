# Security

Sentinel is a **testnet lab**. It is not a production wallet, not a deployment, and not safe for
value at risk; that is documented on the first surface and is not a bug. There is no bug bounty.

**What is in scope for a report:** anything that makes a tool here say more than it establishes —
a verifier result that certifies a bundle `SentinelVault` would refuse, a claim in the README or
the release tree that its own controls do not back, a fixture or key that could be mistaken for
production authority. The project's whole claim is honesty about what it establishes, so a
misstatement is treated as a defect.

**What is known and disclosed, not open:** the native-value ceiling is per action only; a relayer
can drain a funded vault in one transaction; `pause` cannot interrupt that drain; token authority
is not bounded on chain. See `release/README.md`, "What this release does not bound", and
`docs/enforcement-release-v0.3.md`. Reports that restate these will be acknowledged and closed
as disclosed.

**How to report:** open a GitHub issue, or — for anything you would rather not post in the open —
use GitHub's private vulnerability report on this repository's Security tab. Include the command you ran, the output you saw, and the claim
you believe it contradicts. Expect a reply, not a timeline: this is one person's lab.

**Keys:** every key in this repository is a published local test key or is generated in memory by
the demo and discarded. None controls anything. If you believe you have found one that does,
report it as above.
