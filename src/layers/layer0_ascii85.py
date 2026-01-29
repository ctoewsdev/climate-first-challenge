"""
Layer 0: ASCII85 decode.

Input is raw ASCII85 encoded text. Output is decoded bytes.
"""
from helpers import decode_ascii85


def process(data: bytes) -> bytes:
    """Decode Adobe ASCII85 to raw bytes."""
    return decode_ascii85(data)
