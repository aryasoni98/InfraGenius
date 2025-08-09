#!/bin/bash
"""
Deployment script for DevOps/SRE MCP Server
Handles installation, configuration, and deployment across different environments
"""

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Logging functions
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

info() {
    echo -e "${CYAN}[INFO]${NC} $1"
}

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_NAME="devops-sre-mcp-server"
DOCKER_IMAGE="$PROJECT_NAME:latest"
ENVIRONMENT=${ENVIRONMENT:-"development"}
PORT=${PORT:-8000}
OLLAMA_PORT=${OLLAMA_PORT:-11434}

# Default configuration
DEFAULT_CONFIG='{
  "server": {
    "name": "DevOps SRE Platform MCP Server",
    "version": "1.0.0",
    "model": "gpt-oss:latest",
    "performance_optimizations": {
      "enabled": true,
      "parallel_processing": true,
      "caching": true,
      "batch_processing": true
    }
  },
  "ollama": {
    "model": "gpt-oss:latest",
    "base_url": "http://localhost:11434",
    "timeout": 300,
    "parameters": {
      "temperature": 0.1,
      "top_p": 0.9,
      "top_k": 40,
      "repeat_penalty": 1.1,
      "num_ctx": 32768,
      "num_predict": 4096
    }
  },
  "domains": {
    "devops": {"enabled": true, "expertise_level": "senior"},
    "sre": {"enabled": true, "expertise_level": "principal"},
    "cloud": {"enabled": true, "expertise_level": "architect"},
    "platform": {"enabled": true, "expertise_level": "staff"}
  }
}'

# Function to show usage
show_usage() {
    cat << EOF
${PURPLE}DevOps/SRE MCP Server Deployment Script${NC}

Usage: $0 [COMMAND] [OPTIONS]

Commands:
  install     Install dependencies and setup environment
  configure   Configure the server
  build       Build Docker image
  deploy      Deploy the server
  start       Start the server
  stop        Stop the server
  status      Check server status
  logs        Show server logs
  clean       Clean up resources
  update      Update the server
  fine-tune   Run model fine-tuning
  test        Run tests
  help        Show this help message

Options:
  --environment ENV    Set environment (development|staging|production)
  --port PORT         Set server port (default: 8000)
  --model MODEL       Set Ollama model (default: gpt-oss:latest)
  --config FILE       Use custom configuration file
  --docker            Use Docker deployment
  --kubernetes        Use Kubernetes deployment
  --auto-fine-tune    Enable automatic fine-tuning
  --skip-checks       Skip prerequisite checks

Examples:
  $0 install --environment production
  $0 deploy --docker --port 8080
  $0 fine-tune --model gpt-oss-devops:latest
  $0 start --config custom-config.json

EOF
}

# Function to check prerequisites
check_prerequisites() {
    log "Checking prerequisites..."
    
    local missing_deps=()
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        missing_deps+=("python3")
    fi
    
    # Check pip
    if ! command -v pip3 &> /dev/null; then
        missing_deps+=("pip3")
    fi
    
    # Check Docker if needed
    if [ "$USE_DOCKER" = "true" ] && ! command -v docker &> /dev/null; then
        missing_deps+=("docker")
    fi
    
    # Check kubectl if Kubernetes deployment
    if [ "$USE_KUBERNETES" = "true" ] && ! command -v kubectl &> /dev/null; then
        missing_deps+=("kubectl")
    fi
    
    # Check Ollama
    if ! command -v ollama &> /dev/null; then
        warn "Ollama not found. It will be installed automatically."
    fi
    
    if [ ${#missing_deps[@]} -ne 0 ]; then
        error "Missing dependencies: ${missing_deps[*]}"
        info "Please install missing dependencies and try again"
        return 1
    fi
    
    success "Prerequisites check passed"
    return 0
}

# Function to install dependencies
install_dependencies() {
    log "Installing dependencies..."
    
    # Install Ollama if not present
    if ! command -v ollama &> /dev/null; then
        log "Installing Ollama..."
        curl -fsSL https://ollama.ai/install.sh | sh
        success "Ollama installed successfully"
    fi
    
    # Install Python dependencies
    log "Installing Python dependencies..."
    pip3 install -r requirements.txt
    
    # Install development dependencies if in development mode
    if [ "$ENVIRONMENT" = "development" ]; then
        pip3 install -r requirements.txt -e ".[dev]"
        
        # Install pre-commit hooks
        if command -v pre-commit &> /dev/null; then
            pre-commit install
        fi
    fi
    
    success "Dependencies installed successfully"
}

# Function to setup Ollama and models
setup_ollama() {
    log "Setting up Ollama and models..."
    
    # Start Ollama service if not running
    if ! pgrep -f "ollama serve" > /dev/null; then
        log "Starting Ollama service..."
        ollama serve > /dev/null 2>&1 &
        sleep 5
    fi
    
    # Pull base model
    local model=${MODEL_NAME:-"gpt-oss:latest"}
    log "Pulling model: $model"
    
    if ollama pull "$model"; then
        success "Model $model pulled successfully"
    else
        error "Failed to pull model $model"
        return 1
    fi
    
    # Check if fine-tuned model exists
    if [ -f "fine_tuning/devops_dataset.jsonl" ] && [ "$AUTO_FINE_TUNE" = "true" ]; then
        log "Fine-tuning dataset found, running fine-tuning..."
        python3 fine_tuning/fine_tune.py \
            --dataset fine_tuning/devops_dataset.jsonl \
            --output-model gpt-oss-devops:latest \
            --epochs 5
        
        if [ $? -eq 0 ]; then
            success "Fine-tuning completed successfully"
            export ACTIVE_MODEL="gpt-oss-devops:latest"
        else
            warn "Fine-tuning failed, using base model"
            export ACTIVE_MODEL="$model"
        fi
    else
        export ACTIVE_MODEL="$model"
    fi
    
    success "Ollama setup completed"
}

# Function to create configuration
create_configuration() {
    log "Creating configuration..."
    
    if [ ! -f "config.json" ] || [ "$FORCE_CONFIG" = "true" ]; then
        log "Creating default configuration..."
        echo "$DEFAULT_CONFIG" | jq '.' > config.json
        success "Default configuration created"
    else
        info "Configuration file already exists"
    fi
    
    # Update configuration with environment-specific settings
    if [ "$ENVIRONMENT" = "production" ]; then
        log "Applying production configuration..."
        jq '.server.performance_optimizations.enabled = true' config.json > config.tmp && mv config.tmp config.json
        jq '.security.enabled = true' config.json > config.tmp && mv config.tmp config.json
        jq '.monitoring.enabled = true' config.json > config.tmp && mv config.tmp config.json
    fi
    
    success "Configuration setup completed"
}

# Function to build Docker image
build_docker_image() {
    log "Building Docker image..."
    
    if [ "$ENVIRONMENT" = "production" ]; then
        docker build --target production -t "$DOCKER_IMAGE" .
    else
        docker build --target development -t "$DOCKER_IMAGE" .
    fi
    
    if [ $? -eq 0 ]; then
        success "Docker image built successfully: $DOCKER_IMAGE"
    else
        error "Failed to build Docker image"
        return 1
    fi
}

# Function to deploy with Docker
deploy_docker() {
    log "Deploying with Docker..."
    
    # Stop existing container if running
    if docker ps -q -f name="$PROJECT_NAME" | grep -q .; then
        log "Stopping existing container..."
        docker stop "$PROJECT_NAME"
        docker rm "$PROJECT_NAME"
    fi
    
    # Run new container
    log "Starting new container..."
    docker run -d \
        --name "$PROJECT_NAME" \
        -p "$PORT:8000" \
        -p "$OLLAMA_PORT:11434" \
        -v "$(pwd)/config.json:/app/config.json" \
        -v "$(pwd)/logs:/app/logs" \
        -e "ENVIRONMENT=$ENVIRONMENT" \
        -e "AUTO_FINE_TUNE=$AUTO_FINE_TUNE" \
        "$DOCKER_IMAGE"
    
    if [ $? -eq 0 ]; then
        success "Container deployed successfully"
        info "Server available at: http://localhost:$PORT"
    else
        error "Failed to deploy container"
        return 1
    fi
}

# Function to deploy with Kubernetes
deploy_kubernetes() {
    log "Deploying with Kubernetes..."
    
    # Create namespace if it doesn't exist
    kubectl create namespace devops-mcp --dry-run=client -o yaml | kubectl apply -f -
    
    # Apply Kubernetes manifests
    cat << EOF | kubectl apply -f -
apiVersion: apps/v1
kind: Deployment
metadata:
  name: devops-mcp-server
  namespace: devops-mcp
  labels:
    app: devops-mcp-server
spec:
  replicas: 3
  selector:
    matchLabels:
      app: devops-mcp-server
  template:
    metadata:
      labels:
        app: devops-mcp-server
    spec:
      containers:
      - name: devops-mcp-server
        image: $DOCKER_IMAGE
        ports:
        - containerPort: 8000
        - containerPort: 11434
        env:
        - name: ENVIRONMENT
          value: "$ENVIRONMENT"
        - name: AUTO_FINE_TUNE
          value: "$AUTO_FINE_TUNE"
        resources:
          requests:
            memory: "2Gi"
            cpu: "1000m"
          limits:
            memory: "4Gi"
            cpu: "2000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: devops-mcp-service
  namespace: devops-mcp
spec:
  selector:
    app: devops-mcp-server
  ports:
  - name: http
    port: 80
    targetPort: 8000
  - name: ollama
    port: 11434
    targetPort: 11434
  type: LoadBalancer
EOF
    
    if [ $? -eq 0 ]; then
        success "Kubernetes deployment successful"
        
        # Wait for deployment to be ready
        log "Waiting for deployment to be ready..."
        kubectl wait --for=condition=available --timeout=300s deployment/devops-mcp-server -n devops-mcp
        
        # Get service URL
        local service_url=$(kubectl get service devops-mcp-service -n devops-mcp -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
        if [ -n "$service_url" ]; then
            info "Server available at: http://$service_url"
        fi
    else
        error "Failed to deploy to Kubernetes"
        return 1
    fi
}

# Function to start server locally
start_server() {
    log "Starting MCP server locally..."
    
    # Set environment variables
    export MODEL_NAME="${ACTIVE_MODEL:-gpt-oss:latest}"
    export PORT="$PORT"
    export ENVIRONMENT="$ENVIRONMENT"
    
    if [ "$ENVIRONMENT" = "development" ]; then
        python3 server.py --config config.json
    else
        # Use production server with gunicorn
        gunicorn \
            --bind "0.0.0.0:$PORT" \
            --workers 4 \
            --worker-class gevent \
            --worker-connections 1000 \
            --max-requests 1000 \
            --preload \
            --access-logfile logs/access.log \
            --error-logfile logs/error.log \
            --log-level info \
            server:app
    fi
}

# Function to check server status
check_status() {
    log "Checking server status..."
    
    if [ "$USE_DOCKER" = "true" ]; then
        if docker ps -q -f name="$PROJECT_NAME" | grep -q .; then
            success "Docker container is running"
            docker ps -f name="$PROJECT_NAME" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
        else
            warn "Docker container is not running"
        fi
    elif [ "$USE_KUBERNETES" = "true" ]; then
        kubectl get pods -n devops-mcp -l app=devops-mcp-server
        kubectl get services -n devops-mcp
    else
        if pgrep -f "server.py\|gunicorn" > /dev/null; then
            success "Server process is running"
        else
            warn "Server process is not running"
        fi
    fi
    
    # Check if server is responding
    if curl -s -f "http://localhost:$PORT/health" > /dev/null; then
        success "Server is responding to health checks"
    else
        warn "Server is not responding to health checks"
    fi
}

# Function to show logs
show_logs() {
    log "Showing server logs..."
    
    if [ "$USE_DOCKER" = "true" ]; then
        docker logs -f "$PROJECT_NAME"
    elif [ "$USE_KUBERNETES" = "true" ]; then
        kubectl logs -f deployment/devops-mcp-server -n devops-mcp
    else
        if [ -f "logs/server.log" ]; then
            tail -f logs/server.log
        else
            warn "Log file not found"
        fi
    fi
}

# Function to stop server
stop_server() {
    log "Stopping server..."
    
    if [ "$USE_DOCKER" = "true" ]; then
        docker stop "$PROJECT_NAME"
        docker rm "$PROJECT_NAME"
        success "Docker container stopped"
    elif [ "$USE_KUBERNETES" = "true" ]; then
        kubectl delete deployment devops-mcp-server -n devops-mcp
        kubectl delete service devops-mcp-service -n devops-mcp
        success "Kubernetes deployment stopped"
    else
        pkill -f "server.py\|gunicorn" || true
        success "Server process stopped"
    fi
}

# Function to run tests
run_tests() {
    log "Running tests..."
    
    # Install test dependencies
    pip3 install pytest pytest-asyncio pytest-mock
    
    # Run tests
    pytest tests/ -v --tb=short
    
    if [ $? -eq 0 ]; then
        success "All tests passed"
    else
        error "Some tests failed"
        return 1
    fi
}

# Function to run fine-tuning
run_fine_tuning() {
    log "Running model fine-tuning..."
    
    local output_model=${FINE_TUNED_MODEL:-"gpt-oss-devops:latest"}
    
    python3 fine_tuning/fine_tune.py \
        --dataset fine_tuning/devops_dataset.jsonl \
        --output-model "$output_model" \
        --epochs 10 \
        --learning-rate 0.0001
    
    if [ $? -eq 0 ]; then
        success "Fine-tuning completed successfully"
        info "New model available: $output_model"
    else
        error "Fine-tuning failed"
        return 1
    fi
}

# Function to clean up resources
cleanup() {
    log "Cleaning up resources..."
    
    # Stop services
    stop_server
    
    # Clean Docker resources
    if [ "$USE_DOCKER" = "true" ]; then
        docker image prune -f
        docker container prune -f
    fi
    
    # Clean temporary files
    find . -name "*.pyc" -delete
    find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
    rm -rf .pytest_cache/
    rm -rf logs/*.log
    
    success "Cleanup completed"
}

# Function to update server
update_server() {
    log "Updating server..."
    
    # Pull latest code
    git pull origin main
    
    # Update dependencies
    pip3 install -r requirements.txt --upgrade
    
    # Rebuild if using Docker
    if [ "$USE_DOCKER" = "true" ]; then
        build_docker_image
    fi
    
    # Restart server
    stop_server
    sleep 2
    
    if [ "$USE_DOCKER" = "true" ]; then
        deploy_docker
    elif [ "$USE_KUBERNETES" = "true" ]; then
        deploy_kubernetes
    else
        start_server &
    fi
    
    success "Server updated successfully"
}

# Parse command line arguments
COMMAND=""
USE_DOCKER=false
USE_KUBERNETES=false
AUTO_FINE_TUNE=false
SKIP_CHECKS=false
FORCE_CONFIG=false

while [[ $# -gt 0 ]]; do
    case $1 in
        install|configure|build|deploy|start|stop|status|logs|clean|update|fine-tune|test|help)
            COMMAND=$1
            shift
            ;;
        --environment)
            ENVIRONMENT="$2"
            shift 2
            ;;
        --port)
            PORT="$2"
            shift 2
            ;;
        --model)
            MODEL_NAME="$2"
            shift 2
            ;;
        --config)
            CONFIG_FILE="$2"
            shift 2
            ;;
        --docker)
            USE_DOCKER=true
            shift
            ;;
        --kubernetes)
            USE_KUBERNETES=true
            shift
            ;;
        --auto-fine-tune)
            AUTO_FINE_TUNE=true
            shift
            ;;
        --skip-checks)
            SKIP_CHECKS=true
            shift
            ;;
        --force-config)
            FORCE_CONFIG=true
            shift
            ;;
        *)
            error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Show usage if no command provided
if [ -z "$COMMAND" ]; then
    show_usage
    exit 0
fi

# Main execution
main() {
    log "=== DevOps/SRE MCP Server Deployment ==="
    log "Command: $COMMAND"
    log "Environment: $ENVIRONMENT"
    log "Port: $PORT"
    
    # Check prerequisites unless skipped
    if [ "$SKIP_CHECKS" != "true" ] && [ "$COMMAND" != "help" ]; then
        check_prerequisites || exit 1
    fi
    
    # Execute command
    case $COMMAND in
        install)
            install_dependencies
            setup_ollama
            create_configuration
            ;;
        configure)
            create_configuration
            ;;
        build)
            if [ "$USE_DOCKER" = "true" ]; then
                build_docker_image
            else
                warn "Build command requires --docker flag"
            fi
            ;;
        deploy)
            if [ "$USE_DOCKER" = "true" ]; then
                build_docker_image
                deploy_docker
            elif [ "$USE_KUBERNETES" = "true" ]; then
                build_docker_image
                deploy_kubernetes
            else
                setup_ollama
                create_configuration
                start_server &
            fi
            ;;
        start)
            setup_ollama
            start_server
            ;;
        stop)
            stop_server
            ;;
        status)
            check_status
            ;;
        logs)
            show_logs
            ;;
        clean)
            cleanup
            ;;
        update)
            update_server
            ;;
        fine-tune)
            run_fine_tuning
            ;;
        test)
            run_tests
            ;;
        help)
            show_usage
            ;;
        *)
            error "Unknown command: $COMMAND"
            show_usage
            exit 1
            ;;
    esac
    
    if [ $? -eq 0 ]; then
        success "Command '$COMMAND' completed successfully!"
    else
        error "Command '$COMMAND' failed!"
        exit 1
    fi
}

# Run main function
main "$@"
