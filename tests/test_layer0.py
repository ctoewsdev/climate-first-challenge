"""
Tests for layer 0 (ASCII85 decode).
"""
import base64
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from layers.layer0_ascii85 import process


def test_layer0_decode_roundtrip():
    """Decode Adobe ASCII85: roundtrip via base64.a85encode(adobe=True)."""
    plain = b"Hello, layer 0!"
    encoded = base64.a85encode(plain, adobe=True)
    decoded = process(encoded)
    assert decoded == plain, "expected {!r}, got {!r}".format(plain, decoded)


def test_layer0_decode_empty():
    """Empty input decodes to empty bytes."""
    encoded = base64.a85encode(b"", adobe=True)
    decoded = process(encoded)
    assert decoded == b""


if __name__ == "__main__":
    test_layer0_decode_roundtrip()
    test_layer0_decode_empty()
    print("test_layer0 passed.")
