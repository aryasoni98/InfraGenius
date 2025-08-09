#!/bin/bash
"""
Startup script for DevOps/SRE MCP Server
Handles initialization, health checks, and graceful startup
"""

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

# Configuration
OLLAMA_HOST=${OLLAMA_HOST:-"http://localhost:11434"}
MODEL_NAME=${MODEL_NAME:-"gpt-oss:latest"}
FINE_TUNED_MODEL=${FINE_TUNED_MODEL:-"gpt-oss-devops:latest"}
HEALTH_CHECK_TIMEOUT=${HEALTH_CHECK_TIMEOUT:-60}
STARTUP_DELAY=${STARTUP_DELAY:-5}

log "Starting DevOps/SRE/Cloud/Platform Engineering MCP Server"
log "Configuration:"
log "  - Ollama Host: $OLLAMA_HOST"
log "  - Base Model: $MODEL_NAME"
log "  - Fine-tuned Model: $FINE_TUNED_MODEL"
log "  - Health Check Timeout: ${HEALTH_CHECK_TIMEOUT}s"

# Function to check if Ollama is running
check_ollama() {
    log "Checking Ollama service..."
    
    local retries=0
    local max_retries=10
    
    while [ $retries -lt $max_retries ]; do
        if curl -s "$OLLAMA_HOST/api/tags" > /dev/null 2>&1; then
            success "Ollama service is running"
            return 0
        fi
        
        warn "Ollama not ready, attempt $((retries + 1))/$max_retries"
        sleep 5
        retries=$((retries + 1))
    done
    
    error "Ollama service is not responding after $max_retries attempts"
    return 1
}

# Function to check if model exists
check_model() {
    local model=$1
    log "Checking if model '$model' exists..."
    
    if ollama show "$model" > /dev/null 2>&1; then
        success "Model '$model' is available"
        return 0
    else
        warn "Model '$model' not found"
        return 1
    fi
}

# Function to pull model if not exists
ensure_model() {
    local model=$1
    
    if ! check_model "$model"; then
        log "Pulling model '$model'..."
        if ollama pull "$model"; then
            success "Model '$model' pulled successfully"
        else
            error "Failed to pull model '$model'"
            return 1
        fi
    fi
}

# Function to start Ollama service
start_ollama() {
    log "Starting Ollama service..."
    
    # Start Ollama in background
    ollama serve > /var/log/ollama.log 2>&1 &
    OLLAMA_PID=$!
    
    # Wait for Ollama to be ready
    if check_ollama; then
        success "Ollama service started successfully (PID: $OLLAMA_PID)"
        return 0
    else
        error "Failed to start Ollama service"
        return 1
    fi
}

# Function to setup models
setup_models() {
    log "Setting up models..."
    
    # Ensure base model exists
    if ! ensure_model "$MODEL_NAME"; then
        error "Failed to setup base model"
        return 1
    fi
    
    # Check if fine-tuned model exists
    if check_model "$FINE_TUNED_MODEL"; then
        log "Using fine-tuned model: $FINE_TUNED_MODEL"
        export ACTIVE_MODEL="$FINE_TUNED_MODEL"
    else {
        log "Fine-tuned model not found, using base model: $MODEL_NAME"
        export ACTIVE_MODEL="$MODEL_NAME"
    fi
    
    success "Models setup completed"
}

# Function to run fine-tuning if needed
run_fine_tuning() {
    if [ "$AUTO_FINE_TUNE" = "true" ] && [ -f "fine_tuning/devops_dataset.jsonl" ]; then
        log "Auto fine-tuning enabled, starting fine-tuning process..."
        
        python fine_tuning/fine_tune.py \
            --dataset fine_tuning/devops_dataset.jsonl \
            --output-model "$FINE_TUNED_MODEL" \
            --epochs 5
        
        if [ $? -eq 0 ]; then
            success "Fine-tuning completed successfully"
            export ACTIVE_MODEL="$FINE_TUNED_MODEL"
        else
            warn "Fine-tuning failed, using base model"
            export ACTIVE_MODEL="$MODEL_NAME"
        fi
    fi
}

# Function to validate configuration
validate_config() {
    log "Validating configuration..."
    
    # Check if config file exists
    if [ ! -f "config.json" ]; then
        warn "config.json not found, using default configuration"
        cp config.json.example config.json 2>/dev/null || true
    fi
    
    # Validate Python dependencies
    python -c "import mcp, asyncio, json" 2>/dev/null || {
        error "Required Python dependencies not found"
        return 1
    }
    
    success "Configuration validation completed"
}

# Function to setup logging
setup_logging() {
    log "Setting up logging..."
    
    # Create logs directory
    mkdir -p logs
    
    # Set log level
    export LOG_LEVEL=${LOG_LEVEL:-"INFO"}
    
    success "Logging setup completed"
}

# Function to run health checks
health_check() {
    log "Running health checks..."
    
    # Check system resources
    local memory_usage=$(free | grep Mem | awk '{printf "%.1f", $3/$2 * 100.0}')
    local disk_usage=$(df -h / | awk 'NR==2{printf "%s", $5}')
    
    log "System Status:"
    log "  - Memory Usage: ${memory_usage}%"
    log "  - Disk Usage: ${disk_usage}"
    
    # Check if we have enough resources
    if (( $(echo "$memory_usage > 90" | bc -l) )); then
        warn "High memory usage detected: ${memory_usage}%"
    fi
    
    success "Health checks completed"
}

# Function to start MCP server
start_mcp_server() {
    log "Starting MCP Server..."
    
    # Export environment variables
    export MODEL_NAME="$ACTIVE_MODEL"
    export OLLAMA_HOST="$OLLAMA_HOST"
    
    # Start the server
    if [ "$ENVIRONMENT" = "development" ]; then
        log "Starting in development mode..."
        python server.py
    else
        log "Starting in production mode..."
        exec gunicorn \
            --bind 0.0.0.0:8000 \
            --workers ${WORKERS:-4} \
            --worker-class ${WORKER_CLASS:-gevent} \
            --worker-connections ${WORKER_CONNECTIONS:-1000} \
            --max-requests ${MAX_REQUESTS:-1000} \
            --max-requests-jitter ${MAX_REQUESTS_JITTER:-100} \
            --preload \
            --access-logfile - \
            --error-logfile - \
            --log-level ${LOG_LEVEL:-info} \
            server:app
    fi
}

# Cleanup function
cleanup() {
    log "Shutting down services..."
    
    if [ ! -z "$OLLAMA_PID" ]; then
        log "Stopping Ollama service (PID: $OLLAMA_PID)..."
        kill $OLLAMA_PID 2>/dev/null || true
    fi
    
    success "Cleanup completed"
    exit 0
}

# Set up signal handlers
trap cleanup SIGTERM SIGINT

# Main execution flow
main() {
    log "=== DevOps/SRE MCP Server Startup ==="
    
    # Validate configuration
    validate_config || exit 1
    
    # Setup logging
    setup_logging
    
    # Start Ollama service
    start_ollama || exit 1
    
    # Setup models
    setup_models || exit 1
    
    # Run fine-tuning if enabled
    run_fine_tuning
    
    # Run health checks
    health_check
    
    # Small delay for everything to settle
    log "Waiting ${STARTUP_DELAY}s for services to stabilize..."
    sleep $STARTUP_DELAY
    
    success "All services initialized successfully"
    log "Active Model: $ACTIVE_MODEL"
    log "Server starting on port 8000..."
    
    # Start MCP server
    start_mcp_server
}

# Run main function
main "$@"
