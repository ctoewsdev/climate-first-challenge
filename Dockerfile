# Optional: run the pipeline in Docker. Use Python 3.12 to align with CI.
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
