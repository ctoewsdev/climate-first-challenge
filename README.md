# climate-first-challenge

This repo is my submission for a coding challenge, which I’m submitting as part of my job application. It implements the full pipeline (layers 0–6) from the challenge spec (https://www.tomdalling.com/toms-data-onion/)

**AI tooling.** I used AI-assisted development (ChatGPT and Cursor) for this challenge, in line with the instructions to disclose such use.

---

## Prerequisites

- **Python 3.10+** (I run CI on 3.10, 3.12, 3.14; the Docker image uses 3.12.)
- The input file `data/input/layer0_ascii85.txt` is included in the repo.

## Setup

```bash
git clone <repo-url>
cd climate-first-challenge
pip install -r requirements.txt
```

## Run

From the project root (with `PYTHONPATH=src` so imports resolve):

```bash
PYTHONPATH=src python -m src.main
```

Or from `src/` (no `PYTHONPATH` needed):

```bash
cd src && python main.py
```

Use `--no-clear` to keep previous outputs:
`PYTHONPATH=src python -m src.main --no-clear` or `cd src && python main.py --no-clear`.

### Docker (optional)

I’ve added a Dockerfile so you can run the pipeline in a container:

```bash
docker build -t climate-first-challenge .
docker run --rm climate-first-challenge
```

To skip clearing output: `docker run --rm climate-first-challenge python main.py --no-clear`.

To run tests in the container:
`docker run --rm climate-first-challenge python -m pytest ../tests/ -v`
(container `WORKDIR` is `src/`, so tests are at `../tests/`).

### Expected output

On a successful run you’ll see:

```
Clearing output directory...
Running pipeline...
Processing layer 0...
  layer 0 done (0.012s)
Processing layer 1...
  layer 1 done (0.008s)
...
Processing layer 6...
  layer 6 done (0.045s)
Total pipeline runtime: 0.234s
Congratulations! All layers complete. Watch out for drop bears.
```

With `--no-clear`, the “Clearing output directory...” line is omitted. I also log per-layer and total runtimes. You can confirm the expected messages programmatically with `pytest tests/ -v`; the main tests assert on them.

## Tests

```bash
pytest tests/ -v
```

Run from the project root.

## CI

I use GitHub Actions ([.github/workflows/ci.yml](.github/workflows/ci.yml)):

- **On every push:** install deps, run tests (Python 3.10, 3.12, 3.14).
- **On push to `main` or manual “Run workflow”:** run the full pipeline.
- **On manual “Run workflow” only:** build the Docker image.

`data/input/layer0_ascii85.txt` is committed so CI and reviewers can run the pipeline as-is.

## Directory structure

- **`data/input/`** — `layer0_ascii85.txt` (pipeline input). **`data/output/`** — created automatically; layer outputs go here.
- **`src/constants.py`** — Paths, payload markers, and the layer‑4 network filter (IPs, port).
- **`src/helpers.py`** — Shared utilities: decode, payload extraction, checksum; VM helpers (e.g. `read_u8`, `hex_to_bytes`, `HELLO_HEX`).
- **`src/main.py`** — Entry point; ensures `data/output` exists, optionally clears it, runs the pipeline, handles errors.
- **`src/orchestrator.py`** — Runs layers 0–6 in sequence (read → transform → write), with per-layer and total timing.
- **`src/layers/`** — One module per layer: `layer0_ascii85`, `layer1_flip_rotate`, `layer2_parity`, `layer3_xor_dec`, `layer4_packets`, `layer5_aes_ctr`, `layer6_tomtel_vm`.
