import {describe, it} from "node:test";
import assert from "node:assert/strict";
import {CanonicalizationError, canonicalize, type CanonicalValue} from "../src/evaluate/jcs.ts";

/**
 * RFC 8785 canonicalization for the evidence bundle (§5.6).
 *
 * D-010's Python verifier has to reproduce `evidenceHash` byte-for-byte from the published
 * schema alone, so these tests are really about the *specification* the verifier will be
 * written against, not about this implementation. Each one pins a rule the other language
 * must implement identically.
 */

describe("object key ordering", () => {
    it("sorts keys, so insertion order cannot change the hash", () => {
        assert.equal(canonicalize({b: "2", a: "1"}), '{"a":"1","b":"2"}');
        assert.equal(canonicalize({a: "1", b: "2"}), canonicalize({b: "2", a: "1"}));
    });

    it("sorts nested objects too", () => {
        assert.equal(
            canonicalize({outer: {z: "1", a: "2"}, alpha: "x"}),
            '{"alpha":"x","outer":{"a":"2","z":"1"}}',
        );
    });

    it("sorts by code unit, not by locale", () => {
        // A locale-aware sort would put these in a different order in some collations, and
        // the hash would then depend on the machine's locale.
        assert.equal(canonicalize({Z: "1", a: "2"}), '{"Z":"1","a":"2"}');
    });

    it("preserves array order, because order is meaning", () => {
        assert.equal(canonicalize(["b", "a"]), '["b","a"]');
    });
});

describe("numbers are refused, not serialised", () => {
    it("throws on a JSON number anywhere in the tree", () => {
        // The deliberate schema constraint. RFC 8785's number rules are the part two
        // implementations reliably disagree on, so the bundle carries decimal strings.
        assert.throws(() => canonicalize({n: 1 as unknown as CanonicalValue}), CanonicalizationError);
        assert.throws(
            () => canonicalize({deep: {list: [1 as unknown as CanonicalValue]}}),
            /no JSON numbers/,
        );
    });

    it("throws on a bigint too, rather than coercing it", () => {
        // A bigint is the likeliest thing to leak in from this codebase, and silently
        // stringifying it would let the schema drift without anyone noticing.
        assert.throws(() => canonicalize({n: 1n as unknown as CanonicalValue}), CanonicalizationError);
    });

    it("accepts the decimal-string form the schema actually uses", () => {
        assert.equal(canonicalize({valueWei: "1000000000000000000"}), '{"valueWei":"1000000000000000000"}');
    });
});

describe("string escaping (RFC 8785 §3.2.2.2)", () => {
    it("uses the two mandatory escapes and the control shorthands", () => {
        assert.equal(canonicalize('a"b'), '"a\\"b"');
        assert.equal(canonicalize("a\\b"), '"a\\\\b"');
        assert.equal(canonicalize("\b\f\n\r\t"), '"\\b\\f\\n\\r\\t"');
    });

    it("uses \\u00XX for remaining C0 controls", () => {
        assert.equal(canonicalize(""), '"\\u0001"');
        assert.equal(canonicalize(""), '"\\u001f"');
    });

    it("does NOT escape forward slash or non-ASCII", () => {
        // Both are valid JSON either way, and both change the hash. A verifier written
        // against a serialiser that escapes more than this would mismatch on correct data.
        assert.equal(canonicalize("a/b"), '"a/b"');
        assert.equal(canonicalize("café"), '"café"');
        assert.equal(canonicalize("日本"), '"日本"');
    });

    it("escapes unpaired surrogates, as RFC 8785 requires", () => {
        // RFC 8785 §3.2.2.2 defers to ECMAScript's JSON.stringify, which has been well-formed
        // since ES2019 and escapes lone surrogates rather than emitting them raw. Emitting
        // them verbatim produced bytes no conforming implementation would produce and made
        // evidenceHash non-injective, since the raw form is not valid UTF-8. Found by the
        // D-017 review; this test was missing when the fix landed and a mutation caught that.
        for (const lone of ["\uD800", "\uDBFF", "\uDC00", "\uDFFF"]) {
            assert.equal(canonicalize(lone), JSON.stringify(lone), `lone surrogate ${escape(lone)}`);
            assert.equal(canonicalize({k: lone}), JSON.stringify({k: lone}));
        }
        // A WELL-FORMED pair must still pass through unescaped — over-escaping is equally
        // a divergence from the scheme.
        assert.equal(canonicalize("\u{1F600}"), '"\u{1F600}"');
    });

    it("agrees with JSON.stringify across every code point below U+0100", () => {
        // Not a design dependency — the escaping set is written out explicitly so it can be
        // read against the RFC. This checks the claim that the two agree on permitted
        // inputs, which is a fact worth verifying rather than assuming.
        for (let code = 0; code < 0x100; code++) {
            const ch = String.fromCodePoint(code);
            assert.equal(canonicalize(ch), JSON.stringify(ch), `divergence at U+${code.toString(16)}`);
        }
    });
});

describe("keys are restricted to printable ASCII", () => {
    it("rejects a non-ASCII key", () => {
        // RFC 8785 mandates UTF-16 code-unit ordering, which diverges from Python's native
        // code-point sort outside the BMP. Restricting keys makes the two provably identical
        // and the verifier's implementation a plain sorted().
        assert.throws(() => canonicalize({café: "1"}), /printable ASCII/);
        assert.throws(() => canonicalize({"\u{1F600}": "1"}), /printable ASCII/);
    });

    it("still allows any string as a VALUE", () => {
        assert.equal(canonicalize({note: "日本"}), '{"note":"日本"}');
    });
});

describe("primitives and shape", () => {
    it("emits no insignificant whitespace", () => {
        assert.equal(canonicalize({a: ["1", "2"], b: {c: "3"}}), '{"a":["1","2"],"b":{"c":"3"}}');
    });

    it("distinguishes null from absent and from empty", () => {
        assert.equal(canonicalize({a: null}), '{"a":null}');
        assert.equal(canonicalize({a: []}), '{"a":[]}');
        assert.equal(canonicalize({a: {}}), '{"a":{}}');
    });

    it("emits booleans unquoted", () => {
        assert.equal(canonicalize({t: true, f: false}), '{"f":false,"t":true}');
    });

    it("is deterministic across repeated calls", () => {
        const bundle: CanonicalValue = {
            z: ["3", "1"],
            a: {nested: {deep: "true"}},
            m: null,
        };
        assert.equal(canonicalize(bundle), canonicalize(bundle));
    });
});
