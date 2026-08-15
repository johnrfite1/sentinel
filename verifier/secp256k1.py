"""Pure-Python secp256k1 public-key recovery and Ethereum address derivation.

Written from SEC 1 / SEC 2 and the ECDSA public-key recovery procedure. No
third-party dependencies. Performance is irrelevant here: this verifies at most
a handful of signatures per run.
"""

from typing import Optional, Tuple

from keccak import keccak256

# secp256k1 domain parameters (SEC 2, section 2.4.1)
P = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
A = 0
B = 7
GX = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
GY = 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8
G = (GX, GY)

Point = Optional[Tuple[int, int]]  # None is the point at infinity


class RecoveryError(ValueError):
    pass


def _inv(value: int, modulus: int) -> int:
    return pow(value, -1, modulus)


def point_add(p: Point, q: Point) -> Point:
    if p is None:
        return q
    if q is None:
        return p
    x1, y1 = p
    x2, y2 = q
    if x1 == x2:
        if (y1 + y2) % P == 0:
            return None
        lam = (3 * x1 * x1 + A) * _inv(2 * y1, P) % P
    else:
        lam = (y2 - y1) * _inv(x2 - x1, P) % P
    x3 = (lam * lam - x1 - x2) % P
    y3 = (lam * (x1 - x3) - y1) % P
    return (x3, y3)


def point_mul(k: int, p: Point) -> Point:
    k %= N
    result: Point = None
    addend = p
    while k:
        if k & 1:
            result = point_add(result, addend)
        addend = point_add(addend, addend)
        k >>= 1
    return result


def _is_on_curve(x: int, y: int) -> bool:
    return (y * y - (x * x * x + A * x + B)) % P == 0


def parse_signature(signature: str) -> Tuple[int, int, int]:
    """Split a 65-byte 0x-prefixed r||s||v signature into (r, s, v)."""
    raw = bytes.fromhex(signature[2:] if signature.startswith("0x") else signature)
    if len(raw) != 65:
        raise RecoveryError(
            f"expected a 65-byte r||s||v signature, got {len(raw)} bytes"
        )
    r = int.from_bytes(raw[0:32], "big")
    s = int.from_bytes(raw[32:64], "big")
    v = raw[64]
    return r, s, v


def recover_public_key(digest: bytes, r: int, s: int, recovery_id: int) -> Tuple[int, int]:
    """Recover the secp256k1 public key that signed `digest`."""
    if not (1 <= r < N):
        raise RecoveryError("signature r out of range")
    if not (1 <= s < N):
        raise RecoveryError("signature s out of range")
    if recovery_id not in (0, 1, 2, 3):
        raise RecoveryError(f"invalid recovery id {recovery_id}")

    x = r + (recovery_id // 2) * N
    if x >= P:
        raise RecoveryError("recovered x coordinate is not a field element")

    alpha = (x * x * x + A * x + B) % P
    beta = pow(alpha, (P + 1) // 4, P)  # P % 4 == 3, so this is the square root
    if (beta * beta - alpha) % P != 0:
        raise RecoveryError("r is not the x coordinate of a curve point")
    y = beta if (beta % 2) == (recovery_id % 2) else P - beta
    if not _is_on_curve(x, y):
        raise RecoveryError("recovered point is not on the curve")

    e = int.from_bytes(digest, "big")
    r_inv = _inv(r, N)
    # Q = r^-1 * (s*R - e*G)
    point = point_add(point_mul(s, (x, y)), point_mul(N - (e % N), G))
    q = point_mul(r_inv, point)
    if q is None:
        raise RecoveryError("recovered the point at infinity")
    return q


def public_key_to_address(public_key: Tuple[int, int]) -> str:
    x, y = public_key
    serialized = x.to_bytes(32, "big") + y.to_bytes(32, "big")
    return "0x" + keccak256(serialized)[12:].hex()


def recover_address(digest: bytes, signature: str) -> str:
    """Recover the lowercase 0x-prefixed Ethereum address that signed `digest`."""
    r, s, v = parse_signature(signature)
    # Ethereum's eth_sign / EIP-712 convention is v in {27, 28}. Tolerate the
    # raw {0, 1} form as well, since neither the spec nor the samples say which
    # one a receipt carries.
    if v in (27, 28):
        recovery_id = v - 27
    elif v in (0, 1):
        recovery_id = v
    else:
        raise RecoveryError(f"unsupported signature v byte {v}")
    return public_key_to_address(recover_public_key(digest, r, s, recovery_id))


def is_low_s(s: int) -> bool:
    """EIP-2 malleability rule: canonical signatures have s <= N/2."""
    return s <= N // 2
