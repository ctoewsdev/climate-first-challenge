"""
Layer 5: Unwrap an AES-256 key using RFC 3394, then decrypt the payload
using AES-256 in CTR mode.
"""

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes


def _aes_key_unwrap_rfc3394(kek: bytes, wrapped: bytes, iv: bytes) -> bytes:
    """
    Implements the AES Key Wrap algorithm defined in RFC 3394.

    Args:
        kek: 256-bit Key Encryption Key
        wrapped: 40-byte wrapped key
        iv: 8-byte initialization vector
    Returns:
        bytes: The unwrapped AES-256 key
    """
    # number of 8-byte data blocks in the wrapped key
    n = (len(wrapped) // 8) - 1

    # list of 8-byte blocks in the wrapped key
    r = [wrapped[(i + 1) * 8 : (i + 2) * 8] for i in range(n)]

    # first 8-byte block of the wrapped key
    a = wrapped[:8]

    # RFC 3394 uses AES in ECB mode internally (by specification)
    cipher = Cipher(algorithms.AES(kek), modes.ECB()).decryptor()

    # six rounds, processed in reverse order (per RFC 3394)
    for j in range(5, -1, -1):
        for i in range(n - 1, -1, -1):
            # mix the round counter into the integrity register
            t = (n * j) + (i + 1)
            # XOR the integrity register with the current block and decrypt
            b = cipher.update((int.from_bytes(a, "big") ^ t).to_bytes(8, "big") + r[i])
            # update the integrity register and the current block
            a, r[i] = b[:8], b[8:]

    # unwrap is only valid if a matches the expected IV.
    if a != iv:
        raise ValueError("Invalid key unwrap")

    # construct the unwrapped key from the list of 8-byte blocks
    return b"".join(r)


def decrypt_aes_256(payload: bytes) -> bytes:
    """Orchestrates parsing, key unwrap, and payload decryption."""
    offset = 0

    # extract the key encryption key (32 bytes)
    kek = payload[offset : offset + 32]
    offset += 32

    # extract the 64-bit key initialization vector (8 bytes)
    key_iv = payload[offset : offset + 8]
    offset += 8

    # extracts the RFC 3394-wrapped AES-256 key (40 bytes)
    wrapped_key = payload[offset : offset + 40]
    offset += 40

    # extract the 128-bit data initialization vector (16 bytes)
    data_iv = payload[offset : offset + 16]
    offset += 16

    # remaining bytes are the AES-256-CTR ciphertext.
    ciphertext = payload[offset:]

    # unwrap the AES-256 key using RFC 3394
    aes_key = _aes_key_unwrap_rfc3394(kek, wrapped_key, key_iv)

    # initializes AES-256 in Counter Mode.
    cipher = Cipher(algorithms.AES(aes_key), modes.CTR(data_iv))
    decryptor = cipher.decryptor()

    # decrypt the ciphertext using the AES-256-CTR cipher
    decrypted_payload = decryptor.update(ciphertext) + decryptor.finalize()

    return decrypted_payload