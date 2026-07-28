/**
 * RFC 8785 (JSON Canonicalization Scheme) for the evidence bundle (§5.6).
 *
 * §5.6: "EvidenceBundle uses RFC 8785 JSON canonicalization and keccak256 for
 * evidenceHash." The receipt commits to that hash, and D-010's independent Python verifier
 * has to reproduce it byte-for-byte from the published schema alone. Every degree of
 * freedom left here is a place two correct-looking implementations disagree.
 *
 * THE HARD PART OF RFC 8785 IS NUMBERS, SO THE SCHEMA HAS NONE.
 *
 * The specification's most intricate requirement is serialising JSON numbers via the
 * ECMAScript `Number::toString` shortest-round-trip algorithm — the part that makes a
 * conforming implementation genuinely difficult, and the part most likely to differ between
 * a TypeScript evaluator and a Python verifier. Rather than implement it twice and hope,
 * **the evidence bundle contains no JSON numbers at all**: every numeric quantity is a
 * decimal string, which is already how numbers cross this system's RPC boundaries and how
 * a uint256 survives JSON in the first place.
 *
 * `canonicalize` therefore THROWS on a number rather than serialising one. That is a
 * schema constraint enforced mechanically, not a limitation: a number appearing in a bundle
 * means a field was built wrong, and failing loudly now is far cheaper than a verifier
 * mismatch after the corpus has fossilised — which is exactly the feedback D-010 was
 * promoted into v1 to obtain while schemas are still cheap to change.
 *
 * WHAT REMAINS, AND WHY EACH RULE IS HERE:
 *
 *   - Object keys sorted by UTF-16 code unit. RFC 8785 mandates UTF-16 ordering
 *     specifically, which is NOT Python's native `sorted()` on `str` (code points). The two
 *     agree only while keys stay in the Basic Multilingual Plane. Rather than leave that as
 *     a trap for the verifier, ASCII keys are enforced, which makes the orderings provably
 *     identical and the Python side a plain `sorted()`.
 *   - No insignificant whitespace.
 *   - Minimal string escaping, per RFC 8785 §3.2.2.2: only the two mandatory escapes, the
 *     shorthand control escapes, and \u00XX for the remaining C0 controls. Notably NOT
 *     escaping forward slash or non-ASCII — a JSON serialiser that escapes more than this
 *     is still valid JSON and still produces a different hash.
 *   - Arrays keep their order, since order is meaning.
 */

export class CanonicalizationError extends Error {}

/** Values a canonical evidence bundle may contain. Deliberately excludes `number`. */
export type CanonicalValue =
    | string
    | boolean
    | null
    | CanonicalValue[]
    | {[key: string]: CanonicalValue};

const ASCII_KEY = /^[\x20-\x7e]*$/;

/**
 * RFC 8785 §3.2.2.2 string serialisation.
 *
 * Written out rather than delegated to `JSON.stringify` because the two are not the same
 * function, even though they agree on most inputs: the escaping set is what the hash
 * commits to, so it is stated explicitly and can be checked against the RFC line by line.
 * (They do in fact agree for the inputs this schema permits, which the test asserts on a
 * generated sweep of every code point below U+0100 — but "they happen to agree" is a fact
 * to verify, not a design to rely on.)
 */
function serializeString(value: string): string {
    let out = '"';
    for (const ch of value) {
        const code = ch.codePointAt(0)!;
        switch (ch) {
            case '"':
                out += '\\"';
                break;
            case "\\":
                out += "\\\\";
                break;
            case "\b":
                out += "\\b";
                break;
            case "\f":
                out += "\\f";
                break;
            case "\n":
                out += "\\n";
                break;
            case "\r":
                out += "\\r";
                break;
            case "\t":
                out += "\\t";
                break;
            default:
                if (code < 0x20) {
                    out += `\\u${code.toString(16).padStart(4, "0")}`;
                } else {
                    out += ch;
                }
        }
    }
    return `${out}"`;
}

function canonical(value: CanonicalValue, path: string): string {
    if (value === null) return "null";
    if (typeof value === "boolean") return value ? "true" : "false";
    if (typeof value === "string") return serializeString(value);

    if (typeof value === "number" || typeof value === "bigint") {
        throw new CanonicalizationError(
            `${path}: the evidence schema carries no JSON numbers — encode ${String(value)} as a ` +
                `decimal string. RFC 8785 number serialisation is the one part of the scheme two ` +
                `implementations reliably disagree on, and D-010's verifier must reproduce this ` +
                `hash exactly.`,
        );
    }

    if (Array.isArray(value)) {
        return `[${value.map((v, i) => canonical(v, `${path}[${i}]`)).join(",")}]`;
    }

    if (typeof value === "object") {
        const keys = Object.keys(value);
        for (const key of keys) {
            if (!ASCII_KEY.test(key)) {
                throw new CanonicalizationError(
                    `${path}: key ${JSON.stringify(key)} is not printable ASCII. RFC 8785 sorts by ` +
                        `UTF-16 code unit, which diverges from a code-point sort outside the BMP; ` +
                        `restricting keys keeps the ordering provably identical across languages.`,
                );
            }
        }
        // JavaScript's default string sort IS UTF-16 code-unit order, which is what RFC 8785
        // requires. With ASCII keys it coincides with a code-point sort, so the Python
        // verifier's plain `sorted()` agrees.
        const sorted = [...keys].sort();
        const members = sorted.map(
            (k) => `${serializeString(k)}:${canonical(value[k]!, `${path}.${k}`)}`,
        );
        return `{${members.join(",")}}`;
    }

    throw new CanonicalizationError(`${path}: unsupported value of type ${typeof value}`);
}

/** The canonical UTF-8 JSON text of a bundle. This is what gets hashed. */
export function canonicalize(value: CanonicalValue): string {
    return canonical(value, "$");
}
