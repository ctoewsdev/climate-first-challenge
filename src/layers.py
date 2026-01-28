import base64
from collections import Counter
from pathlib import Path
import string

_PAYLOAD_MARKER = "==[ Payload ]=="
_ASCII85_MARKER = "<~"
_ASCII85_MARKER_END = "~>"


def decode_ascii85(payload: bytes) -> bytes:
    """
    Decode Adobe ASCII85-encoded bytes to raw bytes.

    Args:
        payload: Adobe ASCII85-encoded bytes

    Returns:
        Decoded bytes.
    """
    return base64.a85decode(payload, adobe=True)


def get_payload_from_layer_output(path: Path) -> bytes:
    """
    Extract and decode the ASCII85 payload after the '==[ Payload ]==' marker
    in a layer output file.

    Args:
        path: Path to the layer output file.

    Returns:
        Decoded payload as bytes.
    """
    text = path.read_text(encoding="utf-8")
    idx = text.find(_PAYLOAD_MARKER)
    if idx == -1:
        raise ValueError("No '==[ Payload ]' marker found in {}".format(path))

    # Find the ASCII85 block (<~ ... ~>)
    section = text[idx + len(_PAYLOAD_MARKER) :]
    start_marker = section.find(_ASCII85_MARKER)
    if start_marker == -1:
        raise ValueError("No '<~' marker found in payload section")

    end_marker = section.find(_ASCII85_MARKER_END, start_marker)
    if end_marker == -1:
        raise ValueError("No '~>' marker found in payload section")

    # Extract ASCII85 block
    return section[start_marker : end_marker + len(_ASCII85_MARKER_END)]

def flip_and_rotate(data: bytes) -> bytes:
    """
    Flip every second bit, then rotate right by 1 (per byte).

    Applied to each byte:
    - Flip bits at even positions (LSB = position 0) using XOR 0x55
    - Rotate right by 1 bit (circular)
    """
    out = bytearray()
    for b in data:
        flipped = b ^ 0x55
        rotated = (flipped >> 1) | ((flipped & 1) << 7)
        out.append(rotated)
    return bytes(out)


def check_parity(data: bytes) -> bytes:
    """
    Extract data bits from bytes with correct parity.

    For each byte:
    - Bits 7-1 (7 MSBs) are data bits
    - Bit 0 (LSB) is the parity bit
    - Parity is correct if: (count of 1s in data bits) % 2 == parity_bit
    - Only keep bytes with correct parity, extract their 7 data bits
    - Combine all valid 7-bit data chunks into output bytes
    """
    out = bytearray()
    bit_buffer = []

    for byte in data:
        # Extract data bits (bits 7-1) and parity bit (bit 0)
        data_bits = byte >> 1  # 7 bits: 0-127
        parity_bit = byte & 0x01

        # Count 1s in the 7 data bits
        ones_count = bin(data_bits).count('1')

        # Check if parity is correct: odd count -> parity should be 1
        is_valid = (ones_count % 2) == parity_bit

        if is_valid:
            # Add the 7 data bits to the buffer
            for i in range(7):
                bit_buffer.append((data_bits >> (6 - i)) & 1)

            # When we have 8 bits, output a byte
            while len(bit_buffer) >= 8:
                byte_val = 0
                for i in range(8):
                    byte_val |= (bit_buffer.pop(0) << (7 - i))
                out.append(byte_val)

    return bytes(out)


def decrypt_xor(payload: bytes, key_len: int) -> bytes:
    def score_english(bs: bytes) -> int:
        score = 0
        for b in bs:
            if b == 32:                  # space
                score += 5
            elif 65 <= b <= 90:          # A-Z
                score += 3
            elif 97 <= b <= 122:         # a-z
                score += 3
            elif b in (44, 46, 39):      # , . '
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

    # decrypt
    decrypted = bytes(payload[i] ^ key[i % key_len] for i in range(len(payload)))

    # This fixes the consistent 1-bit bias. Ugh!
    return bytes(b ^ 0x01 for b in decrypted)


