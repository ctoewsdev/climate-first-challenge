"""
Shared constants: paths, payload markers, and layer-4 network filter config.

Single source of truth so we can change paths or config in one place.
Paths are relative to project root (parent of src/), resolved via __file__.
"""
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent

# -----------------------------------------------------------------------------
# Paths
# -----------------------------------------------------------------------------
DATA_DIR = _PROJECT_ROOT / "data"
INPUT_DIR = DATA_DIR / "input"
OUTPUT_DIR = DATA_DIR / "output"

# -----------------------------------------------------------------------------
# Payload extraction (layer output files)
# -----------------------------------------------------------------------------
PAYLOAD_MARKER = "==[ Payload ]=="
ASCII85_MARKER = "<~"
ASCII85_MARKER_END = "~>"

# -----------------------------------------------------------------------------
# Layer 4: IPv4/UDP packet filter (SRC_IP, DST_IP, DST_PORT)
# -----------------------------------------------------------------------------
SRC_IP = "10.1.1.10"
DST_IP = "10.1.1.200"
DST_PORT = 42069
