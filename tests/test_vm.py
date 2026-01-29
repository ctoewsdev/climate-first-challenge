"""
Tests for the Tomtel Core i69 VM (layer 6) using the spec's "Hello, world!" example.
"""
import sys
from pathlib import Path

# Allow importing from src
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from layers.layer6_tomtel_vm import run_tomtel_vm
from helpers import HELLO_HEX, hex_to_bytes


def test_hello_world():
    bytecode = hex_to_bytes(HELLO_HEX)
    out = run_tomtel_vm(bytecode)
    assert out == b"Hello, world!", "expected b'Hello, world!', got {!r}".format(out)


if __name__ == "__main__":
    test_hello_world()
    print("test_vm passed.")
