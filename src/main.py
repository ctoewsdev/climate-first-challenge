"""
Entry point for the climate-first coding challenge pipeline.
Runs layers 0-6 in sequence: the output of one layer becomes the input for the
next. All handling and traceback printing happen here; the orchestrator raises 
RuntimeErrors with step context.
"""
from __future__ import print_function  # Py2/3-safe print(file=...); we use .format() not f-strings

import argparse
import sys
import traceback
from constants import OUTPUT_DIR
from orchestrator import run_pipeline


def _clear_output_dir():
    """Remove all files in the output directory before a run."""
    if OUTPUT_DIR.exists():
        for f in OUTPUT_DIR.iterdir():
            if f.is_file():
                f.unlink()


def main(clear=True):
    """
    Entry point: optionally clear output dir, then run the pipeline.
    On any exception, print error + traceback to stderr and exit 1.
    """
    try:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        if clear:
            print("Clearing output directory...")
            _clear_output_dir()

        print("Running pipeline...")
        run_pipeline()

        # Drop bear: classic Aussie tall tale — best enjoyed from a safe distance.
        print("Congratulations! All layers complete. Watch out for drop bears.")


    except Exception as e:
        # Single place for tracebacks: we catch at top level and print here.
        # Orchestrator wraps per-step failures in RuntimeError with context.
        print("Error: {}".format(e), file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-clear", action="store_true", help="Do not clear output directory")
    args = parser.parse_args()
    main(clear=not args.no_clear)
