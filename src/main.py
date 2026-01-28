from __future__ import print_function
import argparse
from pathlib import Path
import sys

from orchestrator import run_pipeline

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_OUTPUT_DIR = _PROJECT_ROOT / "data" / "output"


def _clear_output_dir():
    """Remove all files in the output directory."""
    if _OUTPUT_DIR.exists():
        for f in _OUTPUT_DIR.iterdir():
            if f.is_file():
                f.unlink()


def main(clear=True):
    try:
        if clear:
            print("Clearing output directory...")
            _clear_output_dir()

        print("Running pipeline...")
        run_pipeline()

    except Exception as e:
        print("Error: {}".format(e), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-clear", action="store_true", help="Do not clear output directory")
    args = parser.parse_args()
    main(clear=not args.no_clear)
