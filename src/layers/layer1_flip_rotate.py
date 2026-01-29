"""
Layer 1: flip every second bit, then rotate right by 1 (per byte).

"""


def flip_and_rotate(data: bytes) -> bytes:
    out = bytearray()
    for byte in data:
        # 01010101 so only even bits are flipped
        mask = 0x55
        # XOR every byte with mask
        flipped = byte ^ mask
        # isolate LSB
        lsb = flipped & 1
        # shift bits right by one; insert 0 in MSB
        shifted = flipped >> 1
        # shift LSB to MSB
        rotated = shifted | (lsb << 7)
        out.append(rotated)
    return bytes(out)
