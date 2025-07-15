# Use Python 3.12 slim image for smaller size
FROM python:3.12-slim

# Set build arguments
ARG PYTHON_VERSION=3.12
ARG UV_VERSION=0.4.15

# Install system dependencies for audio processing and healthcheck
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    libsndfile1 \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install --no-cache-dir uv==${UV_VERSION}

# Set working directory
WORKDIR /app

# Copy dependency files first for better layer caching
COPY pyproject.toml uv.lock ./

# Install Python dependencies
RUN uv sync --frozen --no-dev

# Copy application code
COPY src/ src/

# Generate OpenAPI schema for frontend (as root for file permissions)
# This ensures the schema is available even if the container doesn't start
RUN uv run python -c "from src.main import app; import json; print(json.dumps(app.openapi(), indent=2))" > /tmp/openapi.json || echo '{"info":{"title":"API Schema Generation Failed"}}' > /tmp/openapi.json

# Create non-root user for security
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port (Cloud Run uses PORT env variable)
EXPOSE 8000

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Set Python path to include src directory for imports
ENV PYTHONPATH=/app/src

# Run the FastAPI application with uvicorn
# Cloud Run will override PORT if needed
CMD ["uv", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]