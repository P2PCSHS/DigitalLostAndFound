# Build context is the repo root so the image keeps backend/ and frontend/ as
# siblings — app_factory resolves ../frontend as the static folder.
FROM python:3.13-slim

WORKDIR /app

# Install dependencies first so this layer is cached between code changes.
COPY backend/requirements.txt backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt

COPY . .

# Run as a non-root user, and give it the data directory the SQLite volume
# mounts over. A fresh named volume inherits this ownership.
RUN useradd --create-home --uid 1000 appuser \
    && mkdir -p /data \
    && chown -R appuser:appuser /data /app
USER appuser

# gunicorn resolves `run:app` only from the backend directory.
WORKDIR /app/backend

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "run:app"]
