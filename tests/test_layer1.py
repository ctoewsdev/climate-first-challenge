"""
Tests for layer 1 (flip every second bit, rotate right by 1).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from layers.layer1_flip_rotate import flip_and_rotate


def _inverse_flip_rotate(data: bytes) -> bytes:
    """Inverse: rotate left, then XOR 0x55."""
    out = bytearray()
    for b in data:
        rotated = ((b << 1) & 0xFF) | (b >> 7)
        out.append(rotated ^ 0x55)
    return bytes(out)


def test_layer1_flip_rotate_roundtrip():
    """Roundtrip: flip_and_rotate then inverse recovers original."""
    plain = b"Hello, layer 1!"
    transformed = flip_and_rotate(plain)
    back = _inverse_flip_rotate(transformed)
    assert back == plain, "expected {!r}, got {!r}".format(plain, back)


def test_layer1_flip_rotate_empty():
    """Empty input -> empty output."""
    assert flip_and_rotate(b"") == b""


def test_layer1_flip_rotate_known():
    """Known pair: 0x55 -> 0x00 (XOR 0x55 -> 0x00; rotate R 1 -> 0x00)."""
    assert flip_and_rotate(bytes([0x55])) == bytes([0x00])
