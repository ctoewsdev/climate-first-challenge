"""
Shared helpers: decode, payload extraction, checksum; plus layer 6 VM utilities.

Used by layers and orchestrator. Kept at src level (with constants) as
cross-cutting project utilities, not layer logic.
"""
import base64
import struct
from pathlib import Path

from constants import ASCII85_MARKER, ASCII85_MARKER_END, PAYLOAD_MARKER


def decode_ascii85(payload: bytes) -> bytes:
    """
    Decode Adobe ASCII85-encoded bytes to raw bytes.

    Uses adobe=True so that <~ and ~> are handled; input is expected to
    include those delimiters when taken from layer output files.
    """
    return base64.a85decode(payload, adobe=True)


def get_payload_from_layer_output(path: Path):
    """
    Extract the ASCII85 payload block after '==[ Payload ]==' in a layer output file.

    Returns the raw ASCII85 block (including <~ and ~>) as a str. Callers must
    decode via decode_ascii85; if the downstream expects bytes, encode to ASCII
    first (e.g. .encode("ascii")).
    """
    text = path.read_text(encoding="utf-8")
    idx = text.find(PAYLOAD_MARKER)
    if idx == -1:
        raise ValueError("No '==[ Payload ]' marker found in {}".format(path))

    section = text[idx + len(PAYLOAD_MARKER) :]
    start_marker = section.find(ASCII85_MARKER)
    if start_marker == -1:
        raise ValueError("No '<~' marker found in payload section")

    end_marker = section.find(ASCII85_MARKER_END, start_marker)
    if end_marker == -1:
        raise ValueError("No '~>' marker found in payload section")

    return section[start_marker : end_marker + len(ASCII85_MARKER_END)]


def checksum(data: bytes) -> int:
    """Standard internet (ones' complement) checksum. Pad odd length with 0."""
    if len(data) % 2 == 1:
        data += b"\x00"
    s = 0
    for i in range(0, len(data), 2):
        s += (data[i] << 8) + data[i + 1]
    while s >> 16:
        s = (s & 0xFFFF) + (s >> 16)
    return (~s) & 0xFFFF


# -----------------------------------------------------------------------------
# Layer 6 VM: memory access, hex parsing, spec example
# -----------------------------------------------------------------------------


def read_u8(mem: bytearray, addr: int) -> int:
    return mem[addr] if 0 <= addr < len(mem) else 0


def write_u8(mem: bytearray, addr: int, v: int) -> None:
    if 0 <= addr < len(mem):
        mem[addr] = v & 0xFF


def read_u32_le(mem: bytearray, addr: int) -> int:
    if addr < 0 or addr + 4 > len(mem):
        return 0
    return struct.unpack_from("<I", mem, addr)[0]


def hex_to_bytes(hex_str: str) -> bytes:
    """Parse space-separated hex bytes (e.g. '50 48 C2') into bytes."""
    return bytes(int(x, 16) for x in hex_str.split())


HELLO_HEX = (
    "50 48 C2 02 A8 4D 00 00 00 4F 02 50 09 C4 02 02 E1 01 4F 02 C1 22 1D 00 00 00 "
    "48 30 02 58 03 4F 02 B0 29 00 00 00 48 31 02 50 0C C3 02 AA 57 48 02 C1 21 3A 00 00 00 "
    "48 32 02 48 77 02 48 6F 02 48 72 02 48 6C 02 48 64 02 48 21 02 01 "
    "65 6F 33 34 2C"
)
