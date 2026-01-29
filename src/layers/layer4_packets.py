"""
Layer 4: Parse a raw IPv4/UDP byte stream, validate packets, and extract valid
UDP payloads matching SRC_IP, DST_IP, DST_PORT.

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

    # IPv4 headers are at least 20 bytes long
    while offset + 20 <= blob_len:
        first_byte = blob[offset]
        version = first_byte >> 4     # IP version must be 4 (0100)
        ihl = (first_byte & 0x0F) * 4 # IP header length

        # Invalid IP header rejected
        if version != 4 or ihl < 20 or offset + ihl > blob_len:
            offset += 1
            continue

        # slice the IP header from the blob
        ip_hdr = blob[offset : offset + ihl]

        # unpack the IP header fields
        _, _, _, _, _, _, proto, hdr_cksum, src, dst = struct.unpack(
            "!BBHHHBBH4s4s", ip_hdr[:20]
        )

        # recompute the IPv4 header checksum correctly.
        chk_hdr = ip_hdr[:10] + b"\x00\x00" + ip_hdr[12:]
        if checksum(chk_hdr) != hdr_cksum:
            offset += 1
            continue

        # protocol 17 indicates UDP packets; other protocols are rejected
        if proto != 17:
            offset += ihl
            continue

        # break if the packet is too short to contain the 8 byte UDP header
        udp_start = offset + ihl
        if udp_start + 8 > blob_len:
            break

        # unpack the UDP header fields
        udp_hdr = blob[udp_start : udp_start + 8]
        src_port, dst_port, udp_len, udp_cksum = struct.unpack("!HHHH", udp_hdr)

        # valid packet length
        packet_len = ihl + udp_len
        if packet_len <= ihl or offset + packet_len > blob_len:
            offset += 1
            continue

        # slice the UDP payload from the blob
        data = blob[udp_start + 8 : udp_start + udp_len]

        # convert the source and destination IP addresses to strings
        src_ip = socket.inet_ntoa(src)
        dst_ip = socket.inet_ntoa(dst)

        # reject packets that do not match the expected IP addresses and ports
        if src_ip != SRC_IP or dst_ip != DST_IP or dst_port != DST_PORT:
            offset += packet_len
            continue

        # UDP checksum requires even length; pad if necessary
        udp_data = data if len(data) % 2 == 0 else data + b"\x00"

        # create the pseudo-header for the UDP checksum calculation
        pseudo_hdr = (
            src + dst + struct.pack("!BBH", 0, 17, udp_len) + udp_hdr[:6] + b"\x00\x00" + udp_data
        )

        # calculate the UDP checksum using the pseudo-header and UDP data
        # reject corrupt packets
        if udp_cksum != 0 and checksum(pseudo_hdr) != udp_cksum:
            offset += packet_len
            continue

        output.extend(data)
        offset += packet_len

    return bytes(output)
