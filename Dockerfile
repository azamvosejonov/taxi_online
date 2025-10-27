# ============================================ #
# Royal Taxi API - Dockerfile
# Optimized for development and production
# ============================================ #

# Base stage
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_DEFAULT_TIMEOUT=100

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/uploads /app/logs

# Create non-root user and set permissions
RUN groupadd -g 1001 appuser && \
    useradd -u 1001 -g appuser -m -s /bin/bash appuser && \
    chown -R appuser:appuser /app

# ============================================ #
# Development stage
# ============================================ #
FROM base as development

USER appuser

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080", "--reload"]

# ============================================ #
# Production stage
# ============================================ #
FROM base as production

RUN pip install --no-cache-dir gunicorn==21.2.0

USER appuser

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

CMD ["gunicorn", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8080", "--workers", "4", "main:app"]

# ============================================ #
# Worker stage (Celery)
# ============================================ #
FROM base AS worker

RUN pip install --no-cache-dir celery==5.3.6

USER appuser

CMD ["celery", "-A", "main.celery_app", "worker", "--loglevel=info"]

# ============================================ #
# Beat stage (Celery Beat)
# ============================================ #
FROM base AS beat

RUN pip install --no-cache-dir celery==5.3.6

USER appuser

RUN mkdir -p /var/lib/celery/ && \
    chown -R appuser:appuser /var/lib/celery/

CMD ["celery", "-A", "main.celery_app", "beat", "--loglevel=info", "--schedule=/var/lib/celery/celerybeat-schedule"]

# ============================================ #
# Flower stage (Celery monitoring)
# ============================================ #
FROM base AS flower

RUN pip install --no-cache-dir flower==2.0.1

USER appuser

EXPOSE 5555

CMD ["celery", "-A", "main.celery_app", "flower", "--port=5555"]
