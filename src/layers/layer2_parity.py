"""
Layer 2: keep only bytes with correct odd parity, emit 7 data bits each.

Per byte: bits 7–1 = data, bit 0 = parity. Parity is correct when
(count of 1s in data bits) % 2 == parity_bit (odd parity). Invalid
bytes are dropped. We stream 7-bit chunks into 8-bit output bytes
(8 bytes in -> 7 bytes out).
"""


def check_parity(data: bytes) -> bytes:
    out = bytearray()
    bit_buffer = []

    for byte in data:
        data_bits = byte >> 1
        parity_bit = byte & 0x01
        ones_count = bin(data_bits).count("1")
        is_valid = (ones_count % 2) == parity_bit

        if is_valid:
            for i in range(7):
                bit_buffer.append((data_bits >> (6 - i)) & 1)
            while len(bit_buffer) >= 8:
                byte_val = 0
                for i in range(8):
                    byte_val |= (bit_buffer.pop(0) << (7 - i))
                out.append(byte_val)

    return bytes(out)
