"""
Layer 4: extract UDP payload from IPv4/UDP packets matching SRC_IP, DST_IP, DST_PORT.

Scan for IPv4 headers, verify checksum, require UDP; verify UDP checksum when
non-zero. Only matching packets contribute payload. Gotcha: UDP checksum uses
pseudo-header + UDP header (checksum zeroed) + payload (padded to even length).
"""
import socket
import struct

from constants import DST_IP, DST_PORT, SRC_IP

from helpers import checksum


def parse_packets(blob: bytes) -> bytes:
    offset = 0
    output = bytearray()
    blob_len = len(blob)

    while offset + 20 <= blob_len:
        first_byte = blob[offset]
        version = first_byte >> 4
        ihl = (first_byte & 0x0F) * 4

        if version != 4 or ihl < 20 or offset + ihl > blob_len:
            offset += 1
            continue

        ip_hdr = blob[offset : offset + ihl]
        _, _, _, _, _, _, proto, hdr_cksum, src, dst = struct.unpack(
            "!BBHHHBBH4s4s", ip_hdr[:20]
        )

        chk_hdr = ip_hdr[:10] + b"\x00\x00" + ip_hdr[12:]
        if checksum(chk_hdr) != hdr_cksum:
            offset += 1
            continue

        if proto != 17:
            offset += ihl
            continue

        udp_start = offset + ihl
        if udp_start + 8 > blob_len:
            break

        udp_hdr = blob[udp_start : udp_start + 8]
        src_port, dst_port, udp_len, udp_cksum = struct.unpack("!HHHH", udp_hdr)

        packet_len = ihl + udp_len
        if packet_len <= ihl or offset + packet_len > blob_len:
            offset += 1
            continue

        data = blob[udp_start + 8 : udp_start + udp_len]
        src_ip = socket.inet_ntoa(src)
        dst_ip = socket.inet_ntoa(dst)

        if src_ip != SRC_IP or dst_ip != DST_IP or dst_port != DST_PORT:
            offset += packet_len
            continue

        udp_data = data if len(data) % 2 == 0 else data + b"\x00"
        pseudo_hdr = (
            src + dst + struct.pack("!BBH", 0, 17, udp_len) + udp_hdr[:6] + b"\x00\x00" + udp_data
        )
        if udp_cksum != 0 and checksum(pseudo_hdr) != udp_cksum:
            offset += packet_len
            continue

        output.extend(data)
        offset += packet_len

    return bytes(output)
