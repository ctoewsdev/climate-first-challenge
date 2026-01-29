"""
Layer 5: KEK-wrapped AES-256 key + AES-256-CTR ciphertext.

Layout: 32-byte KEK | 8-byte key IV | 40-byte wrapped key (RFC 3394) |
16-byte CTR IV | ciphertext. Unwrap key, then decrypt with AES-256-CTR.
"""
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes


def _aes_key_unwrap_rfc3394(kek: bytes, wrapped: bytes, iv: bytes) -> bytes:
    """RFC 3394 AES key unwrap. 256-bit KEK, 64-bit IV; 8-byte blocks, big-endian."""
    n = (len(wrapped) // 8) - 1
    r = [wrapped[(i + 1) * 8 : (i + 2) * 8] for i in range(n)]
    a = wrapped[:8]
    cipher = Cipher(algorithms.AES(kek), modes.ECB()).decryptor()

    for j in range(5, -1, -1):
        for i in range(n - 1, -1, -1):
            t = (n * j) + (i + 1)
            b = cipher.update((int.from_bytes(a, "big") ^ t).to_bytes(8, "big") + r[i])
            a, r[i] = b[:8], b[8:]

    if a != iv:
        raise ValueError("Invalid key unwrap")
    return b"".join(r)


def decrypt_aes_256(payload: bytes) -> bytes:
    offset = 0
    kek = payload[offset : offset + 32]
    offset += 32
    key_iv = payload[offset : offset + 8]
    offset += 8
    wrapped_key = payload[offset : offset + 40]
    offset += 40
    data_iv = payload[offset : offset + 16]
    offset += 16
    ciphertext = payload[offset:]

    aes_key = _aes_key_unwrap_rfc3394(kek, wrapped_key, key_iv)
    cipher = Cipher(algorithms.AES(aes_key), modes.CTR(data_iv))
    decryptor = cipher.decryptor()
    return decryptor.update(ciphertext) + decryptor.finalize()
