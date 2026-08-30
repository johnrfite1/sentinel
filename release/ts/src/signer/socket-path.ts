import {mkdtempSync} from "node:fs";
import {tmpdir} from "node:os";
import {join} from "node:path";

/**
 * Where a spawned signer's unix socket goes, for every tool that spawns one.
 *
 * THE ARGUMENT (D-052(b), round six L7-3): a unix socket path must fit macOS's 104-byte
 * `sun_path`, and `<REPO>/.sentinel/<name>.sock` does not when REPO is a review worktree — 129
 * bytes from the paths this project actually uses. `connect EINVAL`, before a single fixture is
 * evaluated.
 *
 * A-066 fixed that, and fixed it in ONE of the three places the identical construction appears.
 * `ts/src/corpus/run.ts` got the fallback and thirty lines of reasoning; `ts/src/tools/
 * sample-check.ts` and `ts/src/tools/emit-samples.ts` kept the raw `join(REPO, ".sentinel", …)`
 * and still died from a worktree — which is where a reviewer is told to work, and
 * `sample-check` is John's D-006 adversarial-sampling instrument named as a runnable command in
 * the SIGNED Gate S1 evidence.
 *
 * So the repair is not "add the fallback twice more" — that is generalising the demonstration.
 * It is one implementation the three callers share, so the next caller cannot get it wrong by
 * omission. That is the whole of docs/repair-protocol.md step 2 applied to code rather than to
 * a claim.
 *
 * THE FALLBACK TRIGGERS ON LENGTH, not on being-in-a-worktree, because the byte count is the
 * only thing that breaks. In the live tree the path is short and the behaviour is unchanged, so
 * the committed evidence is untouched.
 *
 * THE FALLBACK GETS ITS OWN PRIVATE DIRECTORY. `startSignerServer` chmods the socket's PARENT to
 * 0700 — unix-socket permissions are checked at connect time and a 0700 parent closes that
 * window however the socket was created, itself an adversarial-review finding. Pointing the
 * signer at a shared system directory asks it to lock down a directory it does not own, which
 * fails with `EPERM`. `mkdtempSync` gives it a fresh private one.
 *
 * @param repoRoot  the repository root the caller resolved
 * @param name      the socket's basename, without `.sock` (e.g. `corpus-8545`)
 * @param overrideDir  an explicit directory, from the caller's own env var if it has one
 */
export function signerSocketPath(repoRoot: string, name: string, overrideDir?: string): string {
    if (overrideDir) return join(overrideDir, `${name}.sock`);
    const preferred = join(repoRoot, ".sentinel", `${name}.sock`);
    if (Buffer.byteLength(preferred) < 100) return preferred;
    return join(mkdtempSync(join(tmpdir(), "sentinel-signer-")), `${name}.sock`);
}
