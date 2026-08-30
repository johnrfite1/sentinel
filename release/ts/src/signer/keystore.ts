import {generatePrivateKey, privateKeyToAccount} from "viem/accounts";
import {digest, domainSeparator, hashReceipt, refusalDigest} from "./eip712.ts";
import type {DecisionReceiptPayload, Hex, RefusalRecord} from "./protocol.ts";

/**
 * Key material for the isolated signer (A-005).
 *
 * This module is where "the signer exposes no generic sign-bytes method" (§3.1) is
 * enforced in the small. A narrow RPC surface is necessary but not sufficient — if the
 * process held an object with a `sign(bytes)` method on it, that narrowness would be one
 * careless import away from being untrue, and the next person who needs "just a quick
 * signature" would find the door already open.
 *
 * So the only thing this keystore can do is sign a DecisionReceiptPayload. Nothing exported
 * here accepts a digest, a hash, or arbitrary bytes. The private key never leaves the
 * closure below, is never returned, and is never logged. `describe()` exists so the process
 * can report which key it is using without that being a way to ask what the key is.
 *
 * KEY SOURCES. `SENTINEL_SIGNER_KEY` in this process's environment, or — when absent — a
 * fresh key generated at boot and never written to disk. The ephemeral path is the better
 * default for a lab: house rule 6 permits only lab-generated testnet keys, and a key that
 * exists solely in one process's memory cannot be committed, copied, or reused. Its cost is
 * that a restart produces a new address and the owner must rotate the vault's signer —
 * which is an operation §3.3(2) already requires be human-only and authenticated, so the
 * cost lands on a path that is supposed to be deliberate.
 */

export interface Keystore {
    readonly address: Hex;
    /**
     * The ONLY signing operation in this process.
     *
     * Takes typed receipt fields, derives the EIP-712 digest itself, and returns a
     * signature over that digest. It cannot be induced to sign anything else: no parameter
     * carries bytes to be signed, and the domain is fixed at construction from the chain
     * and vault this signer serves rather than supplied per call. A per-call domain would
     * let a caller retarget a signature at another chain or vault, which is the precise
     * substitution EIP-712 domain separation exists to prevent.
     */
    signReceipt(receipt: DecisionReceiptPayload): Promise<Hex>;
    /**
     * The second — and only other — signing operation (D-012).
     *
     * Signs a RefusalRecord, which is NOT a §5 payload and NOT an EIP-712 digest. Its digest
     * is domain-separated by a literal ASCII tag (see `refusalDigest`), and every EIP-712
     * digest begins with the bytes 0x1901, so the two preimage spaces cannot collide. A
     * refusal can therefore never be replayed as a receipt of any kind.
     *
     * It is as narrow as `signReceipt`: typed fields in, no parameter through which a caller
     * supplies bytes to be signed. §3.1's "no generic sign-bytes method" is preserved by
     * there being two specific methods rather than one general one.
     */
    signRefusal(record: RefusalRecord): Promise<Hex>;
    describe(): {address: Hex; source: KeySource};
}

export type KeySource = "env" | "ephemeral" | "injected";

export interface KeystoreConfig {
    chainId: bigint;
    vault: Hex;
    /** Injected for tests. Production reads `SENTINEL_SIGNER_KEY` from the environment. */
    privateKey?: Hex;
}

function loadKey(explicit?: Hex): {key: Hex; source: KeySource} {
    const candidates: [value: string | undefined, source: KeySource, label: string][] = [
        [explicit, "injected", "the injected key"],
        [process.env.SENTINEL_SIGNER_KEY, "env", "SENTINEL_SIGNER_KEY"],
    ];
    for (const [value, source, label] of candidates) {
        if (value !== undefined && value !== "") {
            return {key: assertKeyShape(value, label), source};
        }
    }
    return {key: generatePrivateKey(), source: "ephemeral"};
}

function assertKeyShape(value: string, label: string): Hex {
    // Deliberately does not echo the value, not even a prefix of it: a malformed key is
    // still a secret, and error strings travel further than the code that produced them.
    if (!/^0x[0-9a-fA-F]{64}$/.test(value)) {
        throw new Error(`${label} is set but is not a 0x-prefixed 32-byte hex private key`);
    }
    return value as Hex;
}

export function createKeystore(config: KeystoreConfig): Keystore {
    const {key, source} = loadKey(config.privateKey);

    // `assertKeyShape` refuses to echo the key, and then viem undoes that: a 64-hex value
    // outside the secp256k1 order is well-formed to the regex but rejected by
    // `privateKeyToAccount`, whose error text contains the key. Uncaught, Node writes it —
    // in full — to stderr, which is terminal scrollback, supervisor logs, CI output, and
    // the body of a failing test's message. A mistyped or truncated-and-padded key is still
    // a secret. Found by adversarial review; the no-echo discipline is only as good as the
    // noisiest thing on the path.
    let account: ReturnType<typeof privateKeyToAccount>;
    try {
        account = privateKeyToAccount(key);
    } catch {
        throw new Error(
            `the ${source} signing key is 32 bytes of hex but is not a valid secp256k1 ` +
                `private key (out of range). Its value is deliberately not reproduced here.`,
        );
    }

    const address = account.address.toLowerCase() as Hex;
    const domainSep = domainSeparator(config.chainId, config.vault);

    return {
        address,
        async signReceipt(receipt: DecisionReceiptPayload): Promise<Hex> {
            if (receipt.signer.toLowerCase() !== address) {
                // Such a receipt would recover to this key while naming another. The vault
                // checks both halves (`_checkReceipt`), so it is already dead onchain — but
                // producing it at all would put a false statement into an evidence bundle.
                throw new Error("refusing to sign a receipt that names a different signer");
            }
            return account.sign({hash: digest(domainSep, hashReceipt(receipt))});
        },
        async signRefusal(record: RefusalRecord): Promise<Hex> {
            if (record.signer.toLowerCase() !== address) {
                throw new Error("refusing to sign a refusal record that names a different signer");
            }
            return account.sign({hash: refusalDigest(record)});
        },
        describe() {
            return {address, source};
        },
    };
}
