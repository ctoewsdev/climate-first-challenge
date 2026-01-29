"""
Layer 2: filter out bytes with incorrect odd parity, emit 7 data bits each and
reassemble 7-bit data into bytes.
"""


def check_parity(data: bytes) -> bytes:
    out = bytearray()
    # Temporary FIFO buffer holding data bits until a full byte is formed.
    bit_buffer = []

    for byte in data:
        # shift right by 1 to isolate data bits (7-1)
        data_bits = byte >> 1

        # isolate parity bit (0)
        parity_bit = byte & 0x01

        # count number of 1s in data bits
        ones_count = bin(data_bits).count("1")

        # check if parity of total 1s matches parity bit
        is_valid = (ones_count % 2) == parity_bit

        if is_valid:
            # append data bits MSB-first into a rolling bit buffer
            for i in range(7):
              bit_buffer.append((data_bits >> (6 - i)) & 1)

        # if buffer has 8 bits, form a byte and add to output
        while len(bit_buffer) >= 8:
            # Reassemble 8 buffered bits into one output byte
            byte_val = 0
            for i in range(8):
                byte_val |= (bit_buffer.pop(0) << (7 - i))
            out.append(byte_val)

    return bytes(out)
