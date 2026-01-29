"""
Layer 3: XOR decrypt with unknown cycling key (key_len bytes).

Key recovery: split ciphertext into key_len columns, try all 256 key bytes
per column, score with score_english, take best. Then decrypt full payload.

Gotcha: plaintext had a consistent 1-bit bias (extra XOR 0x01). After
recovering the key and XOR-decrypting, we flip that bit; without it,
output is off-by-one (e.g. 'U' vs 'W').
"""


def decrypt_xor(payload: bytes, key_len: int) -> bytes:
    def score_english(bs: bytes) -> int:
        score = 0
        for b in bs:
            if b == 32:
                score += 5
            elif 65 <= b <= 90 or 97 <= b <= 122:
                score += 3
            elif b in (44, 46, 39):
                score += 1
            elif 32 <= b <= 126:
                score += 0
            else:
                score -= 10
        return score

    key = bytearray(key_len)
    for i in range(key_len):
        column = payload[i::key_len]
        best_score = -10**9
        best_key = 0
        for k in range(256):
            decoded = bytes(b ^ k for b in column)
            s = score_english(decoded)
            if s > best_score:
                best_score = s
                best_key = k
        key[i] = best_key

    decrypted = bytes(payload[i] ^ key[i % key_len] for i in range(len(payload)))
    return bytes(b ^ 0x01 for b in decrypted)
