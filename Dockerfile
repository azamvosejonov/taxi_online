FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PATH="/home/appuser/.local/bin:${PATH}"

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
        gcc \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user early to ensure proper permissions
RUN adduser --disabled-password --gecos '' appuser

# Copy requirements and install Python dependencies
COPY --chown=appuser:appuser requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir flower==2.0.1

# Copy project
COPY --chown=appuser:appuser . .

# Switch to non-root user
USER appuser

# Expose ports
EXPOSE 8000 8050

# Default command (can be overridden in docker-compose)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
