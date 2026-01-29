"""
Orchestrates the multi-layer pipeline (Tom's Data Onion layers 0-6).

Each step: read previous output, transform, write next output. We wrap each
step in try/except, raise RuntimeError with step index + message, and chain
the original via 'from exc' so main() can print a full traceback.
"""
from constants import INPUT_DIR, OUTPUT_DIR
from layers import (
    check_parity,
    decode_ascii85,
    decrypt_aes_256,
    decrypt_xor,
    flip_and_rotate,
    get_payload_from_layer_output,
    parse_packets,
    process_layer0,
    run_tomtel_vm,
)


def run_pipeline():
    """
    Run each layer in sequence. Each step is wrapped in try/except: we raise
    RuntimeError with step context + original message, chained via 'from exc'.
    main() prints that error and the full traceback.
    """

    # -------------------------------------------------------------------------
    # STEP 1: Process layer 0 (ASCII85 decode only)
    # -------------------------------------------------------------------------
    print("Processing layer 0...")
    try:
        layer0_input_path = INPUT_DIR / "layer0_ascii85.txt"
        layer0_ascii85_text = layer0_input_path.read_text(encoding="ascii")
        layer0_bytes = process_layer0(layer0_ascii85_text.encode("ascii"))
        (OUTPUT_DIR / "layer0_output.txt").write_bytes(layer0_bytes)
    except Exception as exc:
        raise RuntimeError("Step 1 (Process layer 0) failed: {}".format(exc)) from exc

    # -------------------------------------------------------------------------
    # STEP 2: Process layer 1
    # -------------------------------------------------------------------------
    print("Processing layer 1...")
    try:
        layer1_input_path = OUTPUT_DIR / "layer0_output.txt"
        layer1_ascii85_text = get_payload_from_layer_output(layer1_input_path)
        layer1_bytes = decode_ascii85(layer1_ascii85_text.encode("ascii"))
        layer1_output = flip_and_rotate(layer1_bytes)
        # Persist for next layer
        (OUTPUT_DIR / "layer1_output.txt").write_bytes(layer1_output)
    except Exception as exc:
        raise RuntimeError("Step 2 (Process layer 1) failed: {}".format(exc)) from exc

    # -------------------------------------------------------------------------
    # STEP 3: Process layer 2
    # -------------------------------------------------------------------------
    print("Processing layer 2...")
    try:
        layer2_input_path = OUTPUT_DIR / "layer1_output.txt"
        layer2_ascii85_text = get_payload_from_layer_output(layer2_input_path)
        layer2_bytes = decode_ascii85(layer2_ascii85_text.encode("ascii"))
        layer2_output = check_parity(layer2_bytes)
        # Persist for next layer
        (OUTPUT_DIR / "layer2_output.txt").write_bytes(layer2_output)
    except Exception as exc:
        raise RuntimeError("Step 3 (Process layer 2) failed: {}".format(exc)) from exc

    # -------------------------------------------------------------------------
    # STEP 4: Process layer 3 (XOR decryption; key recovered via frequency analysis)
    # -------------------------------------------------------------------------
    print("Processing layer 3...")
    try:
        layer3_input_path = OUTPUT_DIR / "layer2_output.txt"
        layer3_ascii85_text = get_payload_from_layer_output(layer3_input_path)
        layer3_bytes = decode_ascii85(layer3_ascii85_text.encode("ascii"))
        layer3_output = decrypt_xor(layer3_bytes, 32)
        # Persist for next layer
        (OUTPUT_DIR / "layer3_output.txt").write_bytes(layer3_output)
    except Exception as exc:
        raise RuntimeError("Step 4 (Process layer 3) failed: {}".format(exc)) from exc

    # -------------------------------------------------------------------------
    # STEP 5: Process layer 4
    # -------------------------------------------------------------------------

    print("Processing layer 4...")
    try:
        layer4_input_path = OUTPUT_DIR / "layer3_output.txt"
        layer4_ascii85_text = get_payload_from_layer_output(layer4_input_path)
        layer4_bytes = decode_ascii85(layer4_ascii85_text.encode("ascii"))
        layer4_output = parse_packets(layer4_bytes)
        # Persist for next layer
        (OUTPUT_DIR / "layer4_output.txt").write_bytes(layer4_output)
    except Exception as exc:
        raise RuntimeError("Step 5 (Process layer 4) failed: {}".format(exc)) from exc

    #-------------------------------------------------------------------------
    # STEP 6: Process layer 5
    #-------------------------------------------------------------------------
    print("Processing layer 5...")
    try:
        layer5_input_path = OUTPUT_DIR / "layer4_output.txt"
        layer5_ascii85_text = get_payload_from_layer_output(layer5_input_path)
        layer5_bytes = decode_ascii85(layer5_ascii85_text.encode("ascii"))
        layer5_output = decrypt_aes_256(layer5_bytes)
        # Persist for next layer
        (OUTPUT_DIR / "layer5_output.txt").write_bytes(layer5_output)
    except Exception as exc:
        raise RuntimeError("Step 6 (Process layer 5) failed: {}".format(exc)) from exc

    # -------------------------------------------------------------------------
    # STEP 7: Process layer 6 (Tomtel Core i96 VM)
    # -------------------------------------------------------------------------
    print("Processing layer 6...")
    try:
        layer6_input_path = OUTPUT_DIR / "layer5_output.txt"
        layer6_ascii85_text = get_payload_from_layer_output(layer6_input_path)
        layer6_bytes = decode_ascii85(layer6_ascii85_text.encode("ascii"))
        layer6_output = run_tomtel_vm(layer6_bytes)
        (OUTPUT_DIR / "layer6_output.txt").write_bytes(layer6_output)
    except Exception as exc:
        raise RuntimeError("Step 7 (Process layer 6) failed: {}".format(exc)) from exc