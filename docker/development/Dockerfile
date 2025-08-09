# Development Dockerfile for DevOps/SRE MCP Server
FROM python:3.11-slim

# Set labels
LABEL maintainer="DevOps MCP Team <dev@devops-mcp.com>"
LABEL version="1.0.0"
LABEL description="DevOps/SRE MCP Server - Development Environment"

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONPATH=/app
ENV ENVIRONMENT=development

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    build-essential \
    postgresql-client \
    redis-tools \
    vim \
    htop \
    procps \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Create non-root user for development
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Install development dependencies
RUN pip install --no-cache-dir \
    debugpy \
    pytest-watch \
    black \
    flake8 \
    mypy \
    pre-commit

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p logs tmp uploads && \
    chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose ports
EXPOSE 8000 5678

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Development command with hot reload
CMD ["python", "-m", "debugpy", "--listen", "0.0.0.0:5678", "--wait-for-client", "server.py"]
