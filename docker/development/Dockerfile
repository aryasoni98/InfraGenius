# InfraGenius MCP Server - Development Docker Image
# This connects to local Ollama running on the host machine

FROM python:3.11-slim as base

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
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Create app directory and user
WORKDIR /app
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Copy requirements and install Python dependencies
COPY requirements.docker.txt ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.docker.txt

# Copy application code
COPY . .

# Set ownership
RUN chown -R appuser:appuser /app
USER appuser

# Expose port (Ollama port not needed as it runs on host)
EXPOSE 8000

# Health check (checks both app and connection to host Ollama)
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health && \
        curl -f http://host.docker.internal:11434/api/tags || exit 1

# Start the MCP server
CMD ["python", "mcp_server/server.py"]

# Development stage with additional tools
FROM base as development

# Switch back to root to install dev dependencies
USER root

# Install minimal development dependencies
RUN pip install --no-cache-dir \
    pytest>=7.4.0 \
    black>=23.11.0 \
    flake8>=6.1.0 \
    ipython>=8.17.0 \
    ipdb>=0.13.13

# Development configuration
ENV ENVIRONMENT=development \
    DEBUG=true \
    LOG_LEVEL=DEBUG \
    PYTHONPATH=/app

# Switch back to app user
USER appuser

# Run MCP server in development mode
CMD ["python", "mcp_server/server.py"]

# Production stage
FROM base as production

# Switch back to root to install production dependencies
USER root

# Install gunicorn for production
RUN pip install --no-cache-dir \
    gunicorn==21.2.0 \
    uvicorn[standard]==0.24.0

# Production configuration
ENV ENVIRONMENT=production \
    DEBUG=false \
    LOG_LEVEL=INFO \
    WORKERS=4 \
    WORKER_CLASS=uvicorn.workers.UvicornWorker

# Switch back to app user for security
USER appuser

# Run MCP server directly
CMD ["python", "mcp_server/server.py"]