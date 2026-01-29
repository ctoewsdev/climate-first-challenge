"""
Tests for layer 2 (parity bit: keep valid bytes, emit 7 data bits each).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from layers.layer2_parity import check_parity


def _make_byte(data_bits: int, odd_parity: bool) -> int:
    """Data bits in 7–1; parity in 0. Odd parity: (# of 1s) % 2 == parity_bit."""
    ones = bin(data_bits).count("1")
    parity_bit = 1 if (ones % 2) == 1 else 0
    if not odd_parity:
        parity_bit = 1 - parity_bit
    return ((data_bits & 0x7F) << 1) | (parity_bit & 1)


def test_layer2_empty():
    """Empty input -> empty output."""
    assert check_parity(b"") == b""


def test_layer2_all_zero():
    """8 valid bytes of 0x00 (data=0, parity=0) -> 7 zero bytes."""
    b = _make_byte(0, True)
    assert b == 0x00
    inp = bytes([0x00] * 8)
    out = check_parity(inp)
    assert out == b"\x00" * 7


def test_layer2_all_ones():
    """8 valid bytes 0xFF (data=0x7F, parity=1) -> 7 bytes 0xFF."""
    b = _make_byte(0x7F, True)
    assert b == 0xFF
    inp = bytes([0xFF] * 8)
    out = check_parity(inp)
    assert out == b"\xff" * 7


def test_layer2_invalid_dropped():
    """Invalid parity bytes are dropped; only valid bytes contribute."""
    valid = [_make_byte(0, True)] * 8
    invalid = [_make_byte(0, False)]  # wrong parity
    inp = bytes(valid[:4] + invalid + valid[4:])
    out = check_parity(inp)
    assert len(out) == 7
    assert out == b"\x00" * 7


if __name__ == "__main__":
    test_layer2_empty()
    test_layer2_all_zero()
    test_layer2_all_ones()
    test_layer2_invalid_dropped()
    print("test_layer2 passed.")
