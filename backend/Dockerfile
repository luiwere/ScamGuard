# ==============================================================================
# ScamGuard Backend Dockerfile
# Production-ready Python 3.12 image for FastAPI WebSocket Server
# ==============================================================================

FROM python:3.12-slim

# Set Python environment flags
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

WORKDIR /app

# Install system utilities needed for health checks
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies with layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Create a non-root security user
RUN groupadd -g 1001 scamguard && \
    useradd -u 1001 -g scamguard -s /bin/bash -m scamguard

# Copy application source code and data patterns/scenarios
COPY app/ ./app/
COPY data/ ./data/

# Set ownership to non-root user
RUN chown -R scamguard:scamguard /app

USER scamguard

# Expose FastAPI port
EXPOSE 8000

# Container healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Launch production server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
