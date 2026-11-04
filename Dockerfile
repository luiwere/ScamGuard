# ==============================================================================
# ScamGuard Root Dockerfile (Unified Full-Stack Production Container)
# ==============================================================================
# Stage 1: Build Frontend (React + TypeScript + Vite)
# ------------------------------------------------------------------------------
FROM node:20-alpine AS frontend-builder

WORKDIR /build

COPY frontend/package*.json ./
RUN npm ci --silent || npm install --silent

COPY frontend/tsconfig.json frontend/vite.config.ts frontend/tailwind.config.js frontend/postcss.config.js frontend/index.html ./
COPY frontend/public/ ./public/
COPY frontend/src/ ./src/

RUN npm run build

# ------------------------------------------------------------------------------
# Stage 2: Production Python Backend + Static Asset Server
# ------------------------------------------------------------------------------
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

WORKDIR /app

# Install system utilities needed for health checks
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python backend dependencies
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Create non-root runtime security user
RUN groupadd -g 1001 scamguard && \
    useradd -u 1001 -g scamguard -s /bin/bash -m scamguard

# Copy backend application source code and reference data
COPY backend/app/ ./app/
COPY backend/data/ ./data/

# Copy compiled frontend SPA bundle into static directory
COPY --from=frontend-builder /build/dist ./static/

# Set non-root ownership
RUN chown -R scamguard:scamguard /app

USER scamguard

# Expose unified port
EXPOSE 8000

# Container healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start FastAPI server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
