# DevOps/SRE/Cloud/Platform Engineering MCP Server
# Optimized for production deployment with performance enhancements

FROM python:3.13-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    git \
    build-essential \
    libssl-dev \
    libffi-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Ollama
RUN curl -fsSL https://ollama.ai/install.sh | sh

# Create app directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash devops && \
    chown -R devops:devops /app
USER devops

# Expose ports
EXPOSE 8000 11434

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start script
COPY --chown=devops:devops start.sh /app/
RUN chmod +x /app/start.sh

CMD ["/app/start.sh"]

# Multi-stage build for production
FROM base as production

# Install additional production dependencies
RUN pip install --no-cache-dir \
    gunicorn[gevent]==21.2.0 \
    prometheus-client==0.19.0

# Production configuration
ENV ENVIRONMENT=production \
    WORKERS=4 \
    WORKER_CLASS=gevent \
    WORKER_CONNECTIONS=1000 \
    MAX_REQUESTS=1000 \
    MAX_REQUESTS_JITTER=100 \
    PRELOAD_APP=true

# Use gunicorn for production
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "--worker-class", "gevent", "server:app"]

# Development stage
FROM base as development

# Install development dependencies
RUN pip install --no-cache-dir \
    pytest==7.4.0 \
    pytest-asyncio==0.21.0 \
    black==23.11.0 \
    flake8==6.1.0 \
    mypy==1.7.0 \
    ipython==8.17.0

# Development configuration
ENV ENVIRONMENT=development \
    DEBUG=true \
    LOG_LEVEL=debug

# Use development server
CMD ["python", "server.py"]
