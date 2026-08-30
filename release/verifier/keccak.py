"""Pure-Python Keccak-256 (original Keccak padding, as used by Ethereum).

Written from FIPS 202 / the Keccak reference specification. No third-party
dependencies, and deliberately no code shared with the Sentinel evaluator.

Note the padding byte: Ethereum's keccak256 predates SHA-3 standardisation and
uses the original Keccak pad10*1 with domain byte 0x01, NOT SHA3's 0x06. A
verifier that used hashlib.sha3_256 would disagree with every Ethereum hash.
"""

from typing import List

_ROUNDS = 24

# Round constants for Keccak-f[1600], generated from the LFSR defined in FIPS 202.
_RC = [
    0x0000000000000001, 0x0000000000008082, 0x800000000000808A, 0x8000000080008000,
    0x000000000000808B, 0x0000000080000001, 0x8000000080008081, 0x8000000000008009,
    0x000000000000008A, 0x0000000000000088, 0x0000000080008009, 0x000000008000000A,
    0x000000008000808B, 0x800000000000008B, 0x8000000000008089, 0x8000000000008003,
    0x8000000000008002, 0x8000000000000080, 0x000000000000800A, 0x800000008000000A,
    0x8000000080008081, 0x8000000000008080, 0x0000000080000001, 0x8000000080008008,
]

# Rotation offsets rho[x][y], indexed as lane index x + 5*y.
_ROTC = [
    0, 1, 62, 28, 27,
    36, 44, 6, 55, 20,
    3, 10, 43, 25, 39,
    41, 45, 15, 21, 8,
    18, 2, 61, 56, 14,
]

_MASK64 = (1 << 64) - 1


def _rotl64(value: int, shift: int) -> int:
    shift &= 63
    if shift == 0:
        return value
    return ((value << shift) | (value >> (64 - shift))) & _MASK64


def _keccak_f1600(state: List[int]) -> None:
    """In-place Keccak-f[1600] permutation over 25 64-bit lanes, A[x + 5y]."""
    for rnd in range(_ROUNDS):
        # theta
        c = [
            state[x] ^ state[x + 5] ^ state[x + 10] ^ state[x + 15] ^ state[x + 20]
            for x in range(5)
        ]
        d = [c[(x + 4) % 5] ^ _rotl64(c[(x + 1) % 5], 1) for x in range(5)]
        for x in range(5):
            for y in range(5):
                state[x + 5 * y] ^= d[x]

        # rho and pi
        b = [0] * 25
        for x in range(5):
            for y in range(5):
                b[y + 5 * ((2 * x + 3 * y) % 5)] = _rotl64(
                    state[x + 5 * y], _ROTC[x + 5 * y]
                )

        # chi
        for x in range(5):
            for y in range(5):
                state[x + 5 * y] = b[x + 5 * y] ^ (
                    (~b[((x + 1) % 5) + 5 * y] & _MASK64) & b[((x + 2) % 5) + 5 * y]
                )

        # iota
        state[0] ^= _RC[rnd]


def keccak256(data: bytes) -> bytes:
    """Keccak-256 digest (32 bytes) of `data`."""
    rate = 136  # (1600 - 2*256) / 8
    state = [0] * 25

    # pad10*1 with the original Keccak domain byte 0x01
    padded = bytearray(data)
    padded.append(0x01)
    while len(padded) % rate != 0:
        padded.append(0x00)
    padded[-1] ^= 0x80

    for offset in range(0, len(padded), rate):
        block = padded[offset:offset + rate]
        for i in range(rate // 8):
            state[i] ^= int.from_bytes(block[i * 8:(i + 1) * 8], "little")
        _keccak_f1600(state)

    out = bytearray()
    while len(out) < 32:
        for i in range(rate // 8):
            out += state[i].to_bytes(8, "little")
            if len(out) >= 32:
                break
        else:
            _keccak_f1600(state)
    return bytes(out[:32])


def keccak256_hex(data: bytes) -> str:
    return "0x" + keccak256(data).hex()
