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

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command for development with auto-reload
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# ============================================ #
# Production stage
# ============================================ #
FROM base as production

# Install production dependencies
RUN pip install --no-cache-dir gunicorn==21.2.0

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Command to run the application
CMD ["gunicorn", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000", "--workers", "4", "main:app"]

# ============================================ #
# Worker stage (for Celery)
# ============================================ #
FROM base AS worker

# Install additional dependencies for Celery
RUN pip install --no-cache-dir celery==5.3.6

# Switch to non-root user
USER appuser

# Default command for worker
CMD ["celery", "-A", "main.celery_app", "worker", "--loglevel=info"]

# ============================================ #
# Beat stage (for Celery)
# ============================================ #
FROM base AS beat

# Install additional dependencies for Celery Beat
RUN pip install --no-cache-dir celery==5.3.6

# Switch to non-root user
USER appuser

# Create directory for beat schedule
RUN mkdir -p /var/lib/celery/ && \
    chown -R appuser:appuser /var/lib/celery/

# Default command for beat
CMD ["celery", "-A", "main.celery_app", "beat", "--loglevel=info", "--schedule=/var/lib/celery/celerybeat-schedule"]

# ============================================ #
# Flower stage (for Celery monitoring)
# ============================================ #
FROM base AS flower

# Install Flower for Celery monitoring
RUN pip install --no-cache-dir flower==2.0.1

# Switch to non-root user
USER appuser

# Expose Flower port
EXPOSE 5555

# Default command for flower
CMD ["celery", "-A", "main.celery_app", "flower", "--port=5555"]
CMD ["celery", "-A", "main.celery_app", "flower", "--port=8050"]
