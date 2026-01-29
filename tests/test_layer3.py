"""
Tests for layer 3 (XOR decrypt with key recovery; 1-bit bias correction).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from layers.layer3_xor_dec import decrypt_xor


def _encrypt_xor(plain: bytes, key: bytes) -> bytes:
    """Match layer 3 format: plain XOR 0x01, then XOR cycling key."""
    biased = bytes(b ^ 0x01 for b in plain)
    return bytes(biased[i] ^ key[i % len(key)] for i in range(len(biased)))


def test_layer3_empty():
    """Empty payload -> empty output."""
    assert decrypt_xor(b"", 32) == b""


def test_layer3_roundtrip():
    """Encrypt with 1-byte key; decrypt_xor recovers it. Use plaintext where
    plain XOR 0x01 scores higher than plain (e.g. '!') so recovery picks our key."""
    key = b"\x42"
    plain = b"!" * 50
    cipher = _encrypt_xor(plain, key)
    out = decrypt_xor(cipher, 1)
    assert out == plain, "expected {!r}, got {!r}".format(plain, out)


def test_layer3_short():
    """Short plaintext, key_len=1; same plaintext trick so recovery works."""
    key = b"\xab"
    plain = b"!!!"
    cipher = _encrypt_xor(plain, key)
    out = decrypt_xor(cipher, 1)
    assert out == plain, "expected {!r}, got {!r}".format(plain, out)


if __name__ == "__main__":
    test_layer3_empty()
    test_layer3_roundtrip()
    test_layer3_short()
    print("test_layer3 passed.")
