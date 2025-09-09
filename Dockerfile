# Use Python 3.12 slim image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PORT=8080

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Install Poetry
RUN pip install poetry

# Copy poetry files
COPY pyproject.toml ./

# Configure poetry to not create virtual environment
RUN poetry config virtualenvs.create false

# Install dependencies
RUN poetry install

# Download spaCy model and verify installation
RUN python -m spacy download en_core_web_sm && \
    python -c "import spacy; nlp = spacy.load('en_core_web_sm'); print('spaCy model loaded successfully')"

# Copy model verification script and run it
COPY verify_models.py /tmp/verify_models.py
RUN python /tmp/verify_models.py en_core_web_sm && rm /tmp/verify_models.py

# Copy application code
COPY . .

# Create uploads directory
RUN mkdir -p /app/data/uploads /app/data/temp /app/logs

# Create non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser
RUN chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Add health endpoint to main.py (we'll need to update this)
# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
