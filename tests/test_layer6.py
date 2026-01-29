"""
Tests for layer 6 (Tomtel Core i69 VM) using the spec's "Hello, world!" example.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from helpers import HELLO_HEX, hex_to_bytes
from layers.layer6_tomtel_vm import run_tomtel_vm


def test_layer6_hello_world():
    bytecode = hex_to_bytes(HELLO_HEX)
    out = run_tomtel_vm(bytecode)
    assert out == b"Hello, world!", "expected b'Hello, world!', got {!r}".format(out)


if __name__ == "__main__":
    test_layer6_hello_world()
    print("test_layer6 passed.")
