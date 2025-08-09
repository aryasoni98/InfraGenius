#!/bin/bash
# InfraGenius - One-Click Setup Script
# Auto-detects system and configures accordingly

set -e

# Version and metadata
VERSION="1.0.0"
SCRIPT_NAME="InfraGenius Quick Start"
REPO_URL="https://github.com/your-org/infragenius"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

# Logging functions
log() { echo -e "${BLUE}[$(date +'%H:%M:%S')] $1${NC}"; }
success() { echo -e "${GREEN}✅ $1${NC}"; }
warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
error() { echo -e "${RED}❌ $1${NC}"; exit 1; }
info() { echo -e "${CYAN}ℹ️  $1${NC}"; }
highlight() { echo -e "${WHITE}🎯 $1${NC}"; }

# System detection variables
OS_TYPE=""
OS_VERSION=""
ARCH=""
PACKAGE_MANAGER=""
CONTAINER_RUNTIME=""
KUBERNETES_AVAILABLE=""
PYTHON_VERSION=""
MEMORY_GB=0
CPU_CORES=0
DISK_SPACE_GB=0

# Configuration variables
DEPLOYMENT_TYPE="local"
VERSION_TYPE="opensource"
ENABLE_MONITORING=true
ENABLE_SAMPLE_DATA=false
CUSTOM_DOMAIN=""
LICENSE_KEY=""

show_banner() {
    echo -e "${PURPLE}"
    cat << 'EOF'
╔══════════════════════════════════════════════════════════════════════════════╗
║                              InfraGenius                                    ║
║                         One-Click Setup v1.0.0                             ║
║                                                                              ║
║   🧠 AI-Powered Infrastructure Intelligence Platform                        ║
║   ⚡ Production-Ready • 🔒 Secure • 📊 Observable • 🌍 Multi-Cloud          ║
╚══════════════════════════════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}"
}

detect_system() {
    log "Detecting system configuration..."
    
    # Detect OS
    if [[ "$OSTYPE" == "darwin"* ]]; then
        OS_TYPE="macos"
        OS_VERSION=$(sw_vers -productVersion)
        ARCH=$(uname -m)
        PACKAGE_MANAGER="brew"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        OS_TYPE="linux"
        if [ -f /etc/os-release ]; then
            . /etc/os-release
            OS_VERSION=$VERSION_ID
            if command -v apt &> /dev/null; then
                PACKAGE_MANAGER="apt"
            elif command -v yum &> /dev/null; then
                PACKAGE_MANAGER="yum"
            elif command -v dnf &> /dev/null; then
                PACKAGE_MANAGER="dnf"
            elif command -v pacman &> /dev/null; then
                PACKAGE_MANAGER="pacman"
            fi
        fi
        ARCH=$(uname -m)
    elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
        OS_TYPE="windows"
        PACKAGE_MANAGER="choco"
        ARCH=$(uname -m)
    else
        OS_TYPE="unknown"
    fi
    
    # Detect container runtime
    if command -v docker &> /dev/null; then
        CONTAINER_RUNTIME="docker"
    elif command -v podman &> /dev/null; then
        CONTAINER_RUNTIME="podman"
    fi
    
    # Detect Kubernetes
    if command -v kubectl &> /dev/null; then
        KUBERNETES_AVAILABLE="true"
    fi
    
    # Detect Python
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    elif command -v python &> /dev/null; then
        PYTHON_VERSION=$(python --version | cut -d' ' -f2)
    fi
    
    # Get system resources
    if [[ "$OS_TYPE" == "macos" ]]; then
        MEMORY_GB=$(( $(sysctl -n hw.memsize) / 1024 / 1024 / 1024 ))
        CPU_CORES=$(sysctl -n hw.ncpu)
        DISK_SPACE_GB=$(df -g . | awk 'NR==2 {print $4}')
    elif [[ "$OS_TYPE" == "linux" ]]; then
        MEMORY_GB=$(( $(grep MemTotal /proc/meminfo | awk '{print $2}') / 1024 / 1024 ))
        CPU_CORES=$(nproc)
        DISK_SPACE_GB=$(df -BG . | awk 'NR==2 {print $4}' | sed 's/G//')
    fi
    
    success "System detected successfully"
    info "OS: $OS_TYPE $OS_VERSION ($ARCH)"
    info "Package Manager: $PACKAGE_MANAGER"
    info "Container Runtime: ${CONTAINER_RUNTIME:-Not found}"
    info "Kubernetes: ${KUBERNETES_AVAILABLE:-Not available}"
    info "Python: ${PYTHON_VERSION:-Not found}"
    info "Resources: ${CPU_CORES} CPUs, ${MEMORY_GB}GB RAM, ${DISK_SPACE_GB}GB free"
}

check_system_requirements() {
    log "Checking system requirements..."
    
    local requirements_met=true
    
    # Check minimum requirements
    if [ $CPU_CORES -lt 2 ]; then
        warning "Minimum 2 CPU cores recommended. You have $CPU_CORES."
        requirements_met=false
    fi
    
    if [ $MEMORY_GB -lt 4 ]; then
        warning "Minimum 4GB RAM recommended. You have ${MEMORY_GB}GB."
        requirements_met=false
    fi
    
    if [ $DISK_SPACE_GB -lt 10 ]; then
        warning "Minimum 10GB free disk space recommended. You have ${DISK_SPACE_GB}GB."
        requirements_met=false
    fi
    
    # Check Python version
    if [[ -n "$PYTHON_VERSION" ]]; then
        python_major=$(echo $PYTHON_VERSION | cut -d. -f1)
        python_minor=$(echo $PYTHON_VERSION | cut -d. -f2)
        if [ $python_major -lt 3 ] || ([ $python_major -eq 3 ] && [ $python_minor -lt 8 ]); then
            warning "Python 3.8+ required. You have $PYTHON_VERSION."
            requirements_met=false
        fi
    else
        warning "Python not found. Python 3.8+ is required."
        requirements_met=false
    fi
    
    if [ "$requirements_met" = true ]; then
        success "System requirements check passed"
    else
        warning "Some requirements not met. Installation may not work optimally."
        read -p "Continue anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
}

parse_arguments() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --type)
                DEPLOYMENT_TYPE="$2"
                shift 2
                ;;
            --version)
                VERSION_TYPE="$2"
                shift 2
                ;;
            --license-key)
                LICENSE_KEY="$2"
                shift 2
                ;;
            --domain)
                CUSTOM_DOMAIN="$2"
                shift 2
                ;;
            --monitoring)
                ENABLE_MONITORING=true
                shift
                ;;
            --no-monitoring)
                ENABLE_MONITORING=false
                shift
                ;;
            --sample-data)
                ENABLE_SAMPLE_DATA=true
                shift
                ;;
            --help)
                show_help
                exit 0
                ;;
            *)
                warning "Unknown option: $1"
                shift
                ;;
        esac
    done
}

show_help() {
    cat << EOF
Usage: $0 [OPTIONS]

Options:
    --type TYPE             Deployment type: local, docker, kubernetes (default: local)
    --version VERSION       Version type: opensource, professional (default: opensource)
    --license-key KEY       License key for professional version
    --domain DOMAIN         Custom domain for deployment
    --monitoring            Enable monitoring stack (default: enabled)
    --no-monitoring         Disable monitoring stack
    --sample-data           Include sample data for testing
    --help                  Show this help message

Examples:
    $0                                          # Basic local setup
    $0 --type docker --monitoring              # Docker with monitoring
    $0 --version professional --license-key=KEY # Professional version
    $0 --type kubernetes --domain=api.company.com # Kubernetes with custom domain

EOF
}

install_dependencies() {
    log "Installing required dependencies..."
    
    case $PACKAGE_MANAGER in
        "brew")
            install_macos_dependencies
            ;;
        "apt")
            install_debian_dependencies
            ;;
        "yum"|"dnf")
            install_redhat_dependencies
            ;;
        "pacman")
            install_arch_dependencies
            ;;
        "choco")
            install_windows_dependencies
            ;;
        *)
            error "Unsupported package manager: $PACKAGE_MANAGER"
            ;;
    esac
    
    success "Dependencies installed successfully"
}

install_macos_dependencies() {
    # Update Homebrew
    brew update
    
    # Install required tools
    local tools=(
        "python@3.11"
        "postgresql@15"
        "redis"
        "docker"
        "kubectl"
        "helm"
        "jq"
        "curl"
        "git"
    )
    
    if [[ "$DEPLOYMENT_TYPE" == "kubernetes" || "$DEPLOYMENT_TYPE" == "local" ]]; then
        tools+=("k3d")
    fi
    
    for tool in "${tools[@]}"; do
        if ! brew list "$tool" &> /dev/null; then
            log "Installing $tool..."
            brew install "$tool"
        else
            info "$tool already installed"
        fi
    done
    
    # Start services
    brew services start postgresql@15
    brew services start redis
}

install_debian_dependencies() {
    # Update package lists
    sudo apt update
    
    # Install required packages
    sudo apt install -y \
        python3 \
        python3-pip \
        python3-venv \
        postgresql \
        redis-server \
        docker.io \
        curl \
        jq \
        git \
        build-essential
    
    # Install kubectl
    if ! command -v kubectl &> /dev/null; then
        curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
        sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl
    fi
    
    # Install Helm
    if ! command -v helm &> /dev/null; then
        curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
    fi
    
    # Start services
    sudo systemctl start postgresql
    sudo systemctl start redis-server
    sudo systemctl enable postgresql
    sudo systemctl enable redis-server
}

install_redhat_dependencies() {
    # Install EPEL repository
    sudo $PACKAGE_MANAGER install -y epel-release
    
    # Install required packages
    sudo $PACKAGE_MANAGER install -y \
        python3 \
        python3-pip \
        postgresql-server \
        redis \
        docker \
        curl \
        jq \
        git
    
    # Initialize PostgreSQL
    sudo postgresql-setup --initdb
    sudo systemctl start postgresql
    sudo systemctl start redis
    sudo systemctl enable postgresql
    sudo systemctl enable redis
}

install_arch_dependencies() {
    # Update package database
    sudo pacman -Sy
    
    # Install required packages
    sudo pacman -S --noconfirm \
        python \
        python-pip \
        postgresql \
        redis \
        docker \
        kubectl \
        helm \
        curl \
        jq \
        git
    
    # Initialize PostgreSQL
    sudo -u postgres initdb -D /var/lib/postgres/data
    sudo systemctl start postgresql
    sudo systemctl start redis
    sudo systemctl enable postgresql
    sudo systemctl enable redis
}

install_windows_dependencies() {
    # Install Chocolatey packages
    choco install -y \
        python3 \
        postgresql \
        redis-64 \
        docker-desktop \
        kubernetes-cli \
        kubernetes-helm \
        jq \
        curl \
        git
}

setup_python_environment() {
    log "Setting up Python environment..."
    
    # Create virtual environment
    python3 -m venv venv
    source venv/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install requirements based on version
    if [[ "$VERSION_TYPE" == "professional" ]]; then
        pip install -r requirements.professional.txt
    else
        pip install -r requirements.txt
    fi
    
    success "Python environment setup complete"
}

setup_databases() {
    log "Setting up databases..."
    
    # Setup PostgreSQL
    if [[ "$OS_TYPE" == "macos" ]]; then
        createdb mcpserver 2>/dev/null || true
        psql postgres -c "CREATE USER mcpuser WITH PASSWORD 'mcppass123';" 2>/dev/null || true
        psql postgres -c "GRANT ALL PRIVILEGES ON DATABASE mcpserver TO mcpuser;" 2>/dev/null || true
    else
        sudo -u postgres createdb mcpserver 2>/dev/null || true
        sudo -u postgres psql -c "CREATE USER mcpuser WITH PASSWORD 'mcppass123';" 2>/dev/null || true
        sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE mcpserver TO mcpuser;" 2>/dev/null || true
    fi
    
    # Test database connection
    PGPASSWORD=mcppass123 psql -h localhost -U mcpuser -d mcpserver -c "SELECT version();" > /dev/null
    
    # Test Redis connection
    redis-cli ping > /dev/null
    
    success "Databases setup complete"
}

deploy_application() {
    log "Deploying application..."
    
    case $DEPLOYMENT_TYPE in
        "local")
            deploy_local
            ;;
        "docker")
            deploy_docker
            ;;
        "kubernetes")
            deploy_kubernetes
            ;;
        *)
            error "Unknown deployment type: $DEPLOYMENT_TYPE"
            ;;
    esac
    
    success "Application deployed successfully"
}

deploy_local() {
    log "Deploying locally..."
    
    # Create configuration
    cp config.json config.local.json
    
    # Update configuration for local deployment
    python3 -c "
import json
with open('config.local.json', 'r') as f:
    config = json.load(f)
config['server']['environment'] = 'local'
config['database']['url'] = 'postgresql://mcpuser:mcppass123@localhost:5432/mcpserver'
config['redis']['url'] = 'redis://localhost:6379/0'
with open('config.local.json', 'w') as f:
    json.dump(config, f, indent=2)
"
    
    # Start the server in background
    source venv/bin/activate
    CONFIG_PATH=config.local.json python server.py &
    SERVER_PID=$!
    echo $SERVER_PID > .server.pid
    
    # Wait for server to start
    sleep 10
    
    # Test server
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        success "Server is running at http://localhost:8000"
    else
        error "Server failed to start"
    fi
}

deploy_docker() {
    log "Deploying with Docker..."
    
    # Build Docker image
    docker build -t devops-sre-mcp:latest .
    
    # Create docker-compose file
    cat > docker-compose.local.yml << EOF
version: '3.8'
services:
  mcp-server:
    image: devops-sre-mcp:latest
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://mcpuser:mcppass123@postgres:5432/mcpserver
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - postgres
      - redis
    
  postgres:
    image: postgres:15
    environment:
      - POSTGRES_DB=mcpserver
      - POSTGRES_USER=mcpuser
      - POSTGRES_PASSWORD=mcppass123
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
EOF
    
    # Start services
    docker-compose -f docker-compose.local.yml up -d
    
    # Wait for services to be ready
    sleep 30
    
    # Test server
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        success "Server is running at http://localhost:8000"
    else
        error "Server failed to start"
    fi
}

deploy_kubernetes() {
    log "Deploying to Kubernetes..."
    
    # Check if k3d cluster exists
    if ! k3d cluster list | grep -q "mcp-local"; then
        log "Creating k3d cluster..."
        k3d cluster create mcp-local \
            --port "8000:80@loadbalancer" \
            --agents 1
    fi
    
    # Apply Kubernetes manifests
    kubectl apply -f kubernetes/test/
    
    # Wait for deployment
    kubectl wait --for=condition=available --timeout=300s deployment/mcp-server -n mcp-system
    
    # Test server
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        success "Server is running at http://localhost:8000"
    else
        error "Server failed to start"
    fi
}

setup_monitoring() {
    if [[ "$ENABLE_MONITORING" == "true" ]]; then
        log "Setting up monitoring..."
        
        case $DEPLOYMENT_TYPE in
            "local")
                setup_monitoring_local
                ;;
            "docker")
                setup_monitoring_docker
                ;;
            "kubernetes")
                setup_monitoring_kubernetes
                ;;
        esac
        
        success "Monitoring setup complete"
    fi
}

setup_monitoring_local() {
    # Start Prometheus
    if command -v prometheus &> /dev/null; then
        prometheus --config.file=monitoring/prometheus/prometheus.yml &
        echo $! > .prometheus.pid
    fi
    
    # Start Grafana
    if command -v grafana-server &> /dev/null; then
        grafana-server --config=monitoring/grafana/grafana.ini &
        echo $! > .grafana.pid
    fi
}

setup_monitoring_docker() {
    # Add monitoring services to docker-compose
    cat >> docker-compose.local.yml << EOF
  
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus:/etc/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
    
  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin123
    volumes:
      - grafana_data:/var/lib/grafana
      - ./monitoring/grafana:/etc/grafana/provisioning

volumes:
  grafana_data:
EOF
    
    # Restart docker-compose
    docker-compose -f docker-compose.local.yml up -d
}

setup_monitoring_kubernetes() {
    # Install Prometheus using Helm
    helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
    helm repo update
    
    helm install prometheus prometheus-community/kube-prometheus-stack \
        --namespace monitoring \
        --create-namespace \
        --set grafana.adminPassword=admin123
}

create_sample_data() {
    if [[ "$ENABLE_SAMPLE_DATA" == "true" ]]; then
        log "Creating sample data..."
        
        # Create sample API requests
        curl -X POST http://localhost:8000/analyze \
            -H "Content-Type: application/json" \
            -d '{
                "prompt": "My Kubernetes pods are crashing with OOMKilled errors",
                "domain": "devops",
                "context": "Production cluster with 100+ microservices"
            }' > /dev/null 2>&1 || true
        
        curl -X POST http://localhost:8000/analyze \
            -H "Content-Type: application/json" \
            -d '{
                "prompt": "How do I set up SLOs for my web service?",
                "domain": "sre",
                "context": "E-commerce platform with 99.9% availability target"
            }' > /dev/null 2>&1 || true
        
        success "Sample data created"
    fi
}

show_success_message() {
    echo -e "${GREEN}"
    cat << 'EOF'
╔══════════════════════════════════════════════════════════════════════════════╗
║                            🎉 SETUP COMPLETE! 🎉                            ║
╚══════════════════════════════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}"
    
    highlight "Your InfraGenius platform is now running!"
    echo
    
    info "📊 Service URLs:"
    echo "   🚀 API Server: http://localhost:8000"
    echo "   📋 API Docs: http://localhost:8000/docs"
    echo "   ❤️  Health Check: http://localhost:8000/health"
    
    if [[ "$ENABLE_MONITORING" == "true" ]]; then
        echo "   📈 Grafana: http://localhost:3000 (admin/admin123)"
        echo "   📊 Prometheus: http://localhost:9090"
    fi
    
    echo
    info "🧪 Quick Test:"
    echo '   curl -X POST http://localhost:8000/analyze \'
    echo '     -H "Content-Type: application/json" \'
    echo '     -d '"'"'{"prompt": "Help me debug Kubernetes issues", "domain": "devops"}'"'"
    
    echo
    info "📚 Next Steps:"
    echo "   1. Open http://localhost:8000/docs for API documentation"
    echo "   2. Check out examples/ folder for usage examples"
    echo "   3. Read docs/api/ for detailed API reference"
    
    if [[ "$VERSION_TYPE" == "opensource" ]]; then
        echo "   4. Upgrade to Professional: ./scripts/setup/upgrade-professional.sh"
    fi
    
    echo
    info "🛠️  Management Commands:"
    echo "   Stop: ./scripts/utils/stop.sh"
    echo "   Restart: ./scripts/utils/restart.sh"
    echo "   Logs: ./scripts/utils/logs.sh"
    echo "   Status: ./scripts/utils/status.sh"
    
    echo
    success "Happy DevOps-ing! 🚀"
}

cleanup_on_error() {
    error "Setup failed. Cleaning up..."
    
    # Stop any running processes
    if [ -f .server.pid ]; then
        kill $(cat .server.pid) 2>/dev/null || true
        rm .server.pid
    fi
    
    if [ -f .prometheus.pid ]; then
        kill $(cat .prometheus.pid) 2>/dev/null || true
        rm .prometheus.pid
    fi
    
    if [ -f .grafana.pid ]; then
        kill $(cat .grafana.pid) 2>/dev/null || true
        rm .grafana.pid
    fi
    
    # Stop Docker containers
    if [[ "$DEPLOYMENT_TYPE" == "docker" ]]; then
        docker-compose -f docker-compose.local.yml down 2>/dev/null || true
    fi
    
    # Delete k3d cluster
    if [[ "$DEPLOYMENT_TYPE" == "kubernetes" ]]; then
        k3d cluster delete mcp-local 2>/dev/null || true
    fi
    
    exit 1
}

# Main execution
main() {
    # Set up error handling
    trap cleanup_on_error ERR
    
    show_banner
    
    # Parse command line arguments
    parse_arguments "$@"
    
    # System detection and validation
    detect_system
    check_system_requirements
    
    # Installation steps
    install_dependencies
    setup_python_environment
    setup_databases
    deploy_application
    setup_monitoring
    create_sample_data
    
    # Success message
    show_success_message
}

# Run main function if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
