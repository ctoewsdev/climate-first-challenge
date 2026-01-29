"""
Tests for layer 5 (RFC 3394 key unwrap + AES-256-CTR decryption).

Compatible with older cryptography versions (Python 3.7).
"""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.keywrap import aes_key_wrap

from layers.layer5_aes_ctr import decrypt_aes_256

# RFC 3394 default IV used by aes_key_wrap
_KEY_IV = b"\xA6" * 8


def _build_layer5_payload(plain: bytes, kek: bytes, data_iv: bytes) -> bytes:
    """Build payload: KEK | key_iv | wrapped_key | data_iv | ciphertext."""
    aes_key = os.urandom(32)

    # Wrap AES key using RFC 3394 (legacy API requires backend)
    wrapped_key = aes_key_wrap(kek, aes_key, default_backend())

    # Encrypt plaintext with AES-256-CTR
    cipher = Cipher(
        algorithms.AES(aes_key),
        modes.CTR(data_iv),
        backend=default_backend(),
    )
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(plain) + encryptor.finalize()

    return kek + _KEY_IV + wrapped_key + data_iv + ciphertext


def test_layer5_roundtrip():
    """Roundtrip: wrap + CTR encrypt → decrypt_aes_256 recovers plaintext."""
    kek = os.urandom(32)
    data_iv = os.urandom(16)
    plain = b"Hello, layer 5!"

    payload = _build_layer5_payload(plain, kek, data_iv)
    out = decrypt_aes_256(payload)

    assert out == plain, f"expected {plain!r}, got {out!r}"


def test_layer5_empty_plaintext():
    """Empty plaintext still roundtrips."""
    kek = os.urandom(32)
    data_iv = os.urandom(16)
    plain = b""

    payload = _build_layer5_payload(plain, kek, data_iv)
    out = decrypt_aes_256(payload)

    assert out == plain


if __name__ == "__main__":
    test_layer5_roundtrip()
    test_layer5_empty_plaintext()
    print("test_layer5 passed.")
