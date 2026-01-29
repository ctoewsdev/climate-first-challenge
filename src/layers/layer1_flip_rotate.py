"""
Layer 1: flip every second bit, then rotate right by 1 (per byte).

- Flip: XOR with 0x55 (bits at even positions).
- Rotate right: (x >> 1) | ((x & 1) << 7). LSB becomes MSB.
Gotcha: parameter is 'data' not 'bytes' — shadowing the bytes builtin
leads to "bytes object is not callable" when doing bytes(...).
"""


def flip_and_rotate(data: bytes) -> bytes:
    out = bytearray()
    for b in data:
        flipped = b ^ 0x55
        rotated = (flipped >> 1) | ((flipped & 1) << 7)
        out.append(rotated)
    return bytes(out)
