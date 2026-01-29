"""
Tests for layer 4 (IPv4/UDP packet parsing; filter by SRC_IP, DST_IP, DST_PORT).
"""
import socket
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from constants import DST_IP, DST_PORT, SRC_IP
from helpers import checksum
from layers.layer4_packets import parse_packets


def _build_ip_udp_packet(payload: bytes, src_port: int = 12345) -> bytes:
    """Build IPv4 + UDP packet with SRC_IP, DST_IP, DST_PORT. UDP checksum 0."""
    src = socket.inet_aton(SRC_IP)
    dst = socket.inet_aton(DST_IP)
    ihl = 5
    ip_len = 20 + 8 + len(payload)
    ip_hdr_no_cksum = (
        struct.pack("!BBHHHBB", 0x45, 0, ip_len, 0x1234, 0, 64, 17)
        + b"\x00\x00"
        + src
        + dst
    )
    ip_cksum = checksum(ip_hdr_no_cksum)
    ip_hdr = (
        struct.pack("!BBHHHBBH", 0x45, 0, ip_len, 0x1234, 0, 64, 17, ip_cksum)
        + src
        + dst
    )
    udp_len = 8 + len(payload)
    udp_hdr = struct.pack("!HHHH", src_port, DST_PORT, udp_len, 0)
    return ip_hdr + udp_hdr + payload


def test_layer4_empty():
    """No valid packet -> empty output."""
    assert parse_packets(b"") == b""
    assert parse_packets(b"\x00" * 100) == b""


def test_layer4_single_packet():
    """Single matching IPv4/UDP packet -> payload extracted."""
    payload = b"Hello, layer 4!"
    blob = _build_ip_udp_packet(payload)
    out = parse_packets(blob)
    assert out == payload


def test_layer4_two_packets():
    """Two matching packets -> concatenated payload."""
    a, b = b"abc", b"xyz"
    blob = _build_ip_udp_packet(a, 11111) + _build_ip_udp_packet(b, 22222)
    out = parse_packets(blob)
    assert out == a + b


if __name__ == "__main__":
    test_layer4_empty()
    test_layer4_single_packet()
    test_layer4_two_packets()
    print("test_layer4 passed.")
