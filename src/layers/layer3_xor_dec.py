"""
Layer 3: Recover a repeating 32-byte XOR key and decrypt the payload.
"""


def decrypt_xor(payload: bytes, key_len: int) -> bytes:
    # heuristic to score how closely a byte sequence resembles English text
    def score_english(bs: bytes) -> int:
        score = 0
        for b in bs:
            if b == 32:                            # space character
                score += 5
            elif 65 <= b <= 90 or 97 <= b <= 122:  # upper/lower case letters
                score += 3
            elif b in (44, 46, 39):                # punctuation
                score += 1
            elif 32 <= b <= 126:                   # control/non-printable
                score += 0
            else:                                  # other characters
                score -= 10
        return score

    key = bytearray(key_len)
    for i in range(key_len):
        # group all bytes encrypted with the same key byte (repeating-key XOR)
        column = payload[i::key_len]
        # initialize best score to a very low value
        best_score = -10**9
        # initialize best key to 0
        best_key = 0

        # try all 256 possible values for this key byte
        for k in range(256):
            # XOR each byte in the column with the current key byte
            decoded = bytes(b ^ k for b in column)
            # score the decoded bytes using the English text scoring function
            s = score_english(decoded)

            # keep the key byte that yields the best score
            if s > best_score:
                best_score = s
                best_key = k

        # store the best key byte for this column
        key[i] = best_key

    # decrypt the payload using the recovered key
    decrypted_bytes = bytearray()

    for i, cipher_byte in enumerate(payload):
        # XOR-decrypt using the repeating key
        key_byte = key[i % key_len]
        decrypted_bytes.append(cipher_byte ^ key_byte)

    decrypted = bytes(decrypted_bytes)

    # Correct a common bit bias artifact of repeating-key XOR encryption
    # by XORing each byte with 0x01
    corrected = bytes(b ^ 0x01 for b in decrypted)

    return corrected
