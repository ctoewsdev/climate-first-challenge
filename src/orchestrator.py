from pathlib import Path

from layers import (
    check_parity,
    decode_ascii85,
    decrypt_xor,
    flip_and_rotate,
    get_payload_from_layer_output,
)

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_DATA_DIR = _PROJECT_ROOT / "data"
_INPUT_DIR = _DATA_DIR / "input"
_OUTPUT_DIR = _DATA_DIR / "output"


def run_pipeline():
    # -------------------------------------------------------------------------
    # STEP 1: Process layer 0
    # -------------------------------------------------------------------------
    print("Processing layer 0...")
    layer0_path = _INPUT_DIR / "layer0_ascii85.txt"
    raw = layer0_path.read_text(encoding="ascii")
    layer0_bytes = decode_ascii85(raw.encode('ascii'))

    # Persist for next layer
    (_OUTPUT_DIR  / "layer0_output.txt").write_bytes(layer0_bytes)

    # -------------------------------------------------------------------------
    # STEP 2: Process layer 1
    # -------------------------------------------------------------------------
    print("Processing layer 1...")
    layer1_path = _OUTPUT_DIR  / "layer0_output.txt"
    layer1_bytes = get_payload_from_layer_output(layer1_path)
    layer1_bytes = decode_ascii85(layer1_bytes.encode('ascii'))
    layer1_output = flip_and_rotate(layer1_bytes)

    # Persist for next layer
    (_OUTPUT_DIR  / "layer1_output.txt").write_bytes(layer1_output)

    # -------------------------------------------------------------------------
    # STEP 3: Process layer 2
    # -------------------------------------------------------------------------
    print("Processing layer 2...")
    layer2_path = _OUTPUT_DIR  / "layer1_output.txt"
    layer2_bytes = get_payload_from_layer_output(layer2_path)
    layer2_bytes = decode_ascii85(layer2_bytes.encode('ascii'))
    layer2_output = check_parity(layer2_bytes)

    # Persist for next layer
    (_OUTPUT_DIR  / "layer2_output.txt").write_bytes(layer2_output)

    # -------------------------------------------------------------------------
    # STEP 4: Process layer 3
    # -------------------------------------------------------------------------
    print("Processing layer 3...")
    layer3_path = _OUTPUT_DIR / "layer2_output.txt"
    layer2_bytes = get_payload_from_layer_output(layer3_path)
    layer3_bytes = decode_ascii85(layer2_bytes)
    layer3_output = decrypt_xor(layer3_bytes, 32)

    # Persist for next layer
    (_OUTPUT_DIR / "layer3_output.txt").write_bytes(layer3_output)

    # -------------------------------------------------------------------------
    # STEP 5: Process layer 4
