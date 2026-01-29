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

From project root:

```bash
python -m src.main
```

Or from `src/`:

```bash
cd src && python main.py
```

Use `--no-clear` to keep previous outputs: `python -m src.main --no-clear`.

## Tests

```bash
pytest tests/ -v
```

## CI

GitHub Actions runs on push/PR (see [.github/workflows/ci.yml](.github/workflows/ci.yml)): install deps, run tests, run the pipeline. Use Python 3.10 and 3.12. Ensure `data/input/layer0_ascii85.txt` is committed so CI (and reviewers) can run the pipeline.

## Directory structure

- **`data/input/`** — `layer0_ascii85.txt` (pipeline input). **`data/output/`** — created automatically; layer outputs written here.
- **`src/constants.py`** — Paths, payload markers, layer‑4 network filter (IPs, port).
- **`src/helpers.py`** — Shared utilities: decode, payload extraction, checksum; VM helpers (read_u8, hex_to_bytes, HELLO_HEX, etc.).
- **`src/main.py`** — Entry point; ensures `data/output` exists, optionally clears it, runs pipeline, handles errors.
- **`src/orchestrator.py`** — Runs layers 0–6 in sequence (read → transform → write).
- **`src/layers/`** — One module per layer 0–6: `layer0_ascii85`, `layer1_flip_rotate`, `layer2_parity`, `layer3_xor_dec`, `layer4_packets`, `layer5_aes_ctr`, `layer6_tomtel_vm`.