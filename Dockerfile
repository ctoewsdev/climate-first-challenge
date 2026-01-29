# Optional: run the pipeline in Docker. Python 3.12 (CI-tested; 3.10+ supported).
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ src/
COPY data/ data/
COPY tests/ tests/

# Run from src/ so imports resolve (same as CI).
WORKDIR /app/src
CMD ["python", "main.py"]
