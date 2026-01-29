# climate-first-challenge

## Prerequisites

- **Python 3.7+**
- Input file: `data/input/layer0_ascii85.txt` (included in repo)

## Setup

```bash
git clone <repo-url>
cd climate-first-challenge
pip install -r requirements.txt
```

## Run

From project root (set `PYTHONPATH=src` so imports resolve):

```bash
PYTHONPATH=src python -m src.main
```

Or from `src/` (no `PYTHONPATH` needed):

```bash
cd src && python main.py
```

Use `--no-clear` to keep previous outputs: `PYTHONPATH=src python -m src.main --no-clear` or `cd src && python main.py --no-clear`.

#### Docker (optional)

Build and run the pipeline in a container:

```bash
docker build -t climate-first-challenge .
docker run --rm climate-first-challenge
```

To skip clearing output: `docker run --rm climate-first-challenge python main.py --no-clear`.

To run tests: `docker run --rm climate-first-challenge python -m pytest ../tests/ -v` (container `WORKDIR` is `src/`, so tests live at `../tests/`).

### Expected output

On a successful run you should see:

```
Clearing output directory...
Running pipeline...
Processing layer 0...
Processing layer 1...
...
Processing layer 6...
Congratulations! All layers complete. Watch out for drop bears.
```

With `--no-clear`, the "Clearing output directory..." line is omitted. To confirm this output programmatically, run `pytest tests/ -v`; the main tests assert these messages.

## Tests

```bash
pytest tests/ -v
```

Run from project root.

## CI

GitHub Actions (see [.github/workflows/ci.yml](.github/workflows/ci.yml)):

- **Every push/PR**: install deps, run tests (Python 3.10 and 3.12).
- **Push to `main` or manual “Run workflow”**: run the pipeline.
- **Manual “Run workflow” only**: build Docker image.

Ensure `data/input/layer0_ascii85.txt` is committed so CI (and reviewers) can run the pipeline.

## Directory structure

- **`data/input/`** — `layer0_ascii85.txt` (pipeline input). **`data/output/`** — created automatically; layer outputs written here.
- **`src/constants.py`** — Paths, payload markers, layer‑4 network filter (IPs, port).
- **`src/helpers.py`** — Shared utilities: decode, payload extraction, checksum; VM helpers (read_u8, hex_to_bytes, HELLO_HEX, etc.).
- **`src/main.py`** — Entry point; ensures `data/output` exists, optionally clears it, runs pipeline, handles errors.
- **`src/orchestrator.py`** — Runs layers 0–6 in sequence (read → transform → write).
- **`src/layers/`** — One module per layer 0–6: `layer0_ascii85`, `layer1_flip_rotate`, `layer2_parity`, `layer3_xor_dec`, `layer4_packets`, `layer5_aes_ctr`, `layer6_tomtel_vm`.