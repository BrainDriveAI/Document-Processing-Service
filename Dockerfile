# =======================
# Stage 1 - Builder
# =======================
FROM python:3.12-slim AS builder

ARG ENABLE_CUDA=false

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# System dependencies for building wheels
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install --no-cache-dir poetry==2.2.1

# Copy dependency files
COPY pyproject.toml poetry.lock* /app/

# Configure Poetry
RUN poetry config virtualenvs.create false

# Install dependencies based on CUDA flag
RUN --mount=type=cache,id=poetry-cache,target=/root/.cache/pypoetry \
    --mount=type=cache,id=pip-cache,target=/root/.cache/pip \
    if [ "$ENABLE_CUDA" = "true" ]; then \
        echo "Installing with CUDA support..."; \
        poetry install --without dev --no-interaction --no-ansi --no-root; \
    else \
        echo "Installing CPU-only packages..."; \
        poetry install --without dev --no-interaction --no-ansi --no-root && \
        pip uninstall -y torch torchvision && \
        pip install --no-cache-dir \
            torch==2.7.1+cpu \
            torchvision==0.22.1+cpu \
            --index-url https://download.pytorch.org/whl/cpu; \
    fi

# Clean up unnecessary files
RUN find /usr/local/lib/python3.12 -type d -name "tests" -exec rm -rf {} + 2>/dev/null || true && \
    find /usr/local/lib/python3.12 -type d -name "test" -exec rm -rf {} + 2>/dev/null || true && \
    find /usr/local/lib/python3.12 -type f -name "*.pyc" -delete && \
    find /usr/local/lib/python3.12 -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

# =======================
# Stage 2 - Runtime
# =======================
FROM python:3.12-slim AS runtime

ARG ENABLE_CUDA=false

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PORT=8080 \
    ENABLE_CUDA=${ENABLE_CUDA}

# Install only runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copy only site-packages (not entire lib)
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin/uvicorn /usr/local/bin/uvicorn
COPY --from=builder /usr/local/bin/gunicorn /usr/local/bin/gunicorn

# Add non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Copy local spaCy model
COPY --chown=appuser:appuser spacy_models /app/spacy_models

# Copy application code
COPY --chown=appuser:appuser app /app/app

# Create runtime directories
RUN mkdir -p /app/data/uploads /app/data/temp /app/logs \
    && chown -R appuser:appuser /app

USER appuser

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
