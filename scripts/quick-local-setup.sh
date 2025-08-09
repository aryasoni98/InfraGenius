#!/bin/bash
# InfraGenius Quick Local Setup Script
# Automated setup for local development with Ollama and gpt-oss:latest

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Emojis for better UX
ROCKET="🚀"
CHECKMARK="✅"
WARNING="⚠️"
ERROR="❌"
INFO="ℹ️"
ROBOT="🤖"
PYTHON="🐍"
GEAR="⚙️"
PACKAGE="📦"

# Configuration
OLLAMA_MODEL="gpt-oss:latest"
PYTHON_MIN_VERSION="3.9"
REQUIRED_MEMORY_GB=8

print_header() {
    echo -e "${BLUE}"
    echo "╔════════════════════════════════════════════════════════════════╗"
    echo "║                    InfraGenius Local Setup                    ║"
    echo "║                AI-Powered DevOps & SRE Platform               ║"
    echo "╚════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

print_step() {
    echo -e "${CYAN}${1} ${2}${NC}"
}

print_success() {
    echo -e "${GREEN}${CHECKMARK} ${1}${NC}"
}

print_warning() {
    echo -e "${YELLOW}${WARNING} ${1}${NC}"
}

print_error() {
    echo -e "${RED}${ERROR} ${1}${NC}"
}

print_info() {
    echo -e "${BLUE}${INFO} ${1}${NC}"
}

check_system_requirements() {
    print_step "${GEAR}" "Checking system requirements..."
    
    # Check OS
    OS=$(uname -s)
    print_info "Operating System: $OS"
    
    # Check architecture
    ARCH=$(uname -m)
    print_info "Architecture: $ARCH"
    
    # Check available memory
    if command -v free &> /dev/null; then
        MEMORY_GB=$(free -g | awk '/^Mem:/{print $2}')
    elif command -v vm_stat &> /dev/null; then
        # macOS
        MEMORY_GB=$(echo "$(vm_stat | grep "Pages free" | awk '{print $3}' | sed 's/\.//' ) * 4096 / 1024 / 1024 / 1024" | bc 2>/dev/null || echo "8")
    else
        MEMORY_GB=8  # Assume sufficient
    fi
    
    if [ "$MEMORY_GB" -lt "$REQUIRED_MEMORY_GB" ]; then
        print_warning "Low memory detected: ${MEMORY_GB}GB (recommended: ${REQUIRED_MEMORY_GB}GB+)"
        print_info "You may experience slower performance with large models"
    else
        print_success "Memory check passed: ${MEMORY_GB}GB available"
    fi
    
    # Check disk space
    DISK_SPACE_GB=$(df -BG . | tail -1 | awk '{print $4}' | sed 's/G//')
    if [ "$DISK_SPACE_GB" -lt "20" ]; then
        print_error "Insufficient disk space: ${DISK_SPACE_GB}GB (required: 20GB+)"
        exit 1
    else
        print_success "Disk space check passed: ${DISK_SPACE_GB}GB available"
    fi
}

check_python() {
    print_step "${PYTHON}" "Checking Python installation..."
    
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 not found. Please install Python 3.9+ from https://python.org"
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)
    
    if [ "$PYTHON_MAJOR" -lt "3" ] || ([ "$PYTHON_MAJOR" -eq "3" ] && [ "$PYTHON_MINOR" -lt "9" ]); then
        print_error "Python $PYTHON_VERSION found, but Python 3.9+ required"
        print_info "Please upgrade Python: https://python.org/downloads"
        exit 1
    fi
    
    print_success "Python $PYTHON_VERSION found"
    
    # Check pip
    if ! python3 -m pip --version &> /dev/null; then
        print_error "pip not found. Please install pip"
        exit 1
    fi
    
    print_success "pip found"
}

check_ollama() {
    print_step "${ROBOT}" "Checking Ollama setup..."
    
    # Check if Ollama is installed
    if ! command -v ollama &> /dev/null; then
        print_error "Ollama not found! Please install Ollama first:"
        echo ""
        echo -e "${YELLOW}Installation commands:${NC}"
        echo -e "  ${BLUE}macOS:${NC}     brew install ollama"
        echo -e "  ${BLUE}Linux:${NC}     curl -fsSL https://ollama.ai/install.sh | sh"
        echo -e "  ${BLUE}Windows:${NC}   winget install ollama"
        echo ""
        echo -e "${CYAN}Or visit: https://ollama.ai${NC}"
        exit 1
    fi
    
    print_success "Ollama installed"
    
    # Check if Ollama service is running
    print_info "Checking Ollama service..."
    if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        print_success "Ollama service is running on port 11434"
    else
        print_warning "Ollama service not running on port 11434"
        print_info "Please start Ollama service:"
        echo -e "  ${YELLOW}ollama serve${NC}"
        echo ""
        print_info "Attempting to start Ollama service..."
        
        # Try to start Ollama
        if pgrep -x "ollama" > /dev/null; then
            print_info "Ollama process found but not responding on port 11434"
            print_info "You may need to restart Ollama manually"
        else
            print_info "Starting Ollama service..."
            ollama serve &
            OLLAMA_PID=$!
            print_info "Ollama service started (PID: $OLLAMA_PID)"
            
            # Wait for Ollama to start
            print_info "Waiting for Ollama to initialize..."
            for i in {1..30}; do
                if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
                    break
                fi
                sleep 1
                echo -n "."
            done
            echo ""
            
            if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
                print_error "Failed to start Ollama service"
                print_info "Please start Ollama manually: ollama serve"
                exit 1
            fi
            
            print_success "Ollama service is ready"
        fi
    fi
    
    # Pull required model
    print_info "Downloading AI model: $OLLAMA_MODEL..."
    print_warning "This may take several minutes (model is ~4GB)"
    
    if ollama list | grep -q "$OLLAMA_MODEL"; then
        print_success "Model $OLLAMA_MODEL already available"
    else
        if ollama pull "$OLLAMA_MODEL"; then
            print_success "Model $OLLAMA_MODEL downloaded successfully"
        else
            print_warning "Failed to download $OLLAMA_MODEL, trying alternative..."
            
            # Try alternative models
            for alt_model in "llama3.1:latest" "qwen2.5-coder:latest" "mistral:latest"; do
                print_info "Trying alternative model: $alt_model"
                if ollama pull "$alt_model"; then
                    print_success "Alternative model $alt_model downloaded"
                    OLLAMA_MODEL="$alt_model"
                    break
                fi
            done
            
            if ! ollama list | grep -q "$OLLAMA_MODEL"; then
                print_error "Failed to download any AI model"
                exit 1
            fi
        fi
    fi
    
    # Test model
    print_info "Testing AI model..."
    if echo "Hello" | ollama run "$OLLAMA_MODEL" > /dev/null 2>&1; then
        print_success "AI model is working correctly"
    else
        print_warning "AI model test failed, but continuing..."
    fi
}

setup_python_environment() {
    print_step "${PACKAGE}" "Setting up Python environment..."
    
    # Create virtual environment
    if [ -d "venv" ]; then
        print_info "Virtual environment already exists"
    else
        print_info "Creating virtual environment..."
        python3 -m venv venv
        print_success "Virtual environment created"
    fi
    
    # Activate virtual environment
    print_info "Activating virtual environment..."
    source venv/bin/activate
    
    # Upgrade pip
    print_info "Upgrading pip..."
    python -m pip install --upgrade pip setuptools wheel
    
    # Install dependencies
    if [ -f "requirements.txt" ]; then
        print_info "Installing dependencies..."
        pip install -r requirements.txt
        print_success "Dependencies installed"
    else
        print_warning "requirements.txt not found, installing basic dependencies..."
        pip install fastapi uvicorn httpx pydantic
    fi
    
    # Install development dependencies
    if [ -f "requirements-dev.txt" ]; then
        print_info "Installing development dependencies..."
        pip install -r requirements-dev.txt
        print_success "Development dependencies installed"
    fi
    
    # Install pre-commit hooks
    if command -v pre-commit &> /dev/null; then
        print_info "Setting up pre-commit hooks..."
        pre-commit install
        print_success "Pre-commit hooks installed"
    fi
    
    # Install package in development mode
    if [ -f "setup.py" ] || [ -f "pyproject.toml" ]; then
        print_info "Installing InfraGenius in development mode..."
        pip install -e .
        print_success "InfraGenius installed in development mode"
    fi
}

setup_configuration() {
    print_step "${GEAR}" "Setting up configuration..."
    
    # Create config from example
    if [ -f "mcp_server/config.json" ]; then
        print_info "Configuration file already exists"
    elif [ -f "mcp_server/config.json.example" ]; then
        print_info "Creating configuration from example..."
        cp mcp_server/config.json.example mcp_server/config.json
        
        # Update model in config if we used alternative
        if [ "$OLLAMA_MODEL" != "gpt-oss:latest" ]; then
            print_info "Updating configuration to use $OLLAMA_MODEL"
            sed -i.bak "s/gpt-oss:latest/$OLLAMA_MODEL/g" mcp_server/config.json
            rm mcp_server/config.json.bak 2>/dev/null || true
        fi
        
        print_success "Configuration created"
    else
        print_info "Creating basic configuration..."
        mkdir -p mcp_server
        cat > mcp_server/config.json << EOF
{
  "server": {
    "host": "127.0.0.1",
    "port": 8000,
    "debug": true
  },
  "ollama": {
    "base_url": "http://127.0.0.1:11434",
    "model": "$OLLAMA_MODEL"
  },
  "domains": {
    "devops": {"enabled": true},
    "sre": {"enabled": true},
    "cloud": {"enabled": true},
    "platform": {"enabled": true}
  }
}
EOF
        print_success "Basic configuration created"
    fi
    
    # Create .env file
    if [ ! -f ".env" ]; then
        print_info "Creating .env file..."
        cat > .env << EOF
# InfraGenius Local Development Environment
INFRAGENIUS_HOST=127.0.0.1
INFRAGENIUS_PORT=8000
INFRAGENIUS_DEBUG=true
INFRAGENIUS_LOG_LEVEL=INFO

OLLAMA_BASE_URL=http://127.0.0.1:11434
OLLAMA_MODEL=$OLLAMA_MODEL

# Development settings
DEVELOPMENT_MODE=true
AUTO_RELOAD=true
CORS_ENABLED=true
EOF
        print_success ".env file created"
    fi
    
    # Create logs directory
    mkdir -p logs
    print_success "Logs directory created"
}

setup_cursor_integration() {
    print_step "${GEAR}" "Setting up Cursor MCP integration..."
    
    # Create .cursor directory
    mkdir -p .cursor
    
    # Create MCP servers configuration
    cat > .cursor/mcp-servers.json << EOF
{
  "mcpServers": {
    "infragenius": {
      "command": "python",
      "args": ["-m", "mcp_server.cursor_integration"],
      "env": {
        "OLLAMA_BASE_URL": "http://127.0.0.1:11434",
        "OLLAMA_MODEL": "$OLLAMA_MODEL",
        "INFRAGENIUS_CONFIG": "./mcp_server/config.json"
      },
      "description": "InfraGenius DevOps/SRE AI Assistant"
    }
  }
}
EOF
    
    print_success "Cursor MCP configuration created"
    print_info "To use in Cursor: Install MCP extension and restart Cursor"
}

run_health_check() {
    print_step "${CHECKMARK}" "Running health check..."
    
    # Check Python environment
    if python --version > /dev/null 2>&1; then
        print_success "Python environment: OK"
    else
        print_error "Python environment: FAILED"
    fi
    
    # Check Ollama service
    if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        print_success "Ollama service: OK"
    else
        print_error "Ollama service: FAILED"
    fi
    
    # Check model availability
    if ollama list | grep -q "$OLLAMA_MODEL"; then
        print_success "AI model ($OLLAMA_MODEL): OK"
    else
        print_error "AI model: FAILED"
    fi
    
    # Check configuration
    if python -c "import json; json.load(open('mcp_server/config.json'))" 2>/dev/null; then
        print_success "Configuration: OK"
    else
        print_error "Configuration: FAILED"
    fi
    
    # Test import
    if python -c "import mcp_server" 2>/dev/null; then
        print_success "InfraGenius import: OK"
    else
        print_warning "InfraGenius import: May not work (install with 'pip install -e .')"
    fi
}

start_server() {
    print_step "${ROCKET}" "Starting InfraGenius server..."
    
    print_info "Starting server in background..."
    
    # Start server in background
    if [ -f "mcp_server/server.py" ]; then
        python mcp_server/server.py &
        SERVER_PID=$!
        print_info "Server started (PID: $SERVER_PID)"
    else
        print_warning "Server file not found, starting with uvicorn..."
        uvicorn mcp_server.server:app --host 127.0.0.1 --port 8000 &
        SERVER_PID=$!
        print_info "Server started with uvicorn (PID: $SERVER_PID)"
    fi
    
    # Wait for server to start
    print_info "Waiting for server to start..."
    for i in {1..30}; do
        if curl -s http://localhost:8000/health > /dev/null 2>&1; then
            break
        fi
        sleep 1
        echo -n "."
    done
    echo ""
    
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        print_success "Server is running!"
        print_info "Health check: http://localhost:8000/health"
        print_info "API documentation: http://localhost:8000/docs"
        
        # Test API
        print_info "Testing API..."
        RESPONSE=$(curl -s -X POST http://localhost:8000/analyze \
            -H "Content-Type: application/json" \
            -d '{"prompt": "Test analysis", "domain": "devops"}' | head -c 100)
        
        if [ -n "$RESPONSE" ]; then
            print_success "API test successful!"
        else
            print_warning "API test failed, but server is running"
        fi
    else
        print_error "Server failed to start properly"
        print_info "Check logs: tail -f logs/infragenius.log"
    fi
}

print_completion() {
    print_success "InfraGenius setup completed successfully!"
    echo ""
    echo -e "${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║                        🎉 Setup Complete! 🎉                   ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${CYAN}${ROCKET} Quick Start Commands:${NC}"
    echo -e "  ${YELLOW}Health Check:${NC}     curl http://localhost:8000/health"
    echo -e "  ${YELLOW}API Docs:${NC}         open http://localhost:8000/docs"
    echo -e "  ${YELLOW}Test Analysis:${NC}    curl -X POST http://localhost:8000/analyze \\"
    echo -e "                      -H 'Content-Type: application/json' \\"
    echo -e "                      -d '{\"prompt\": \"My pods are crashing\", \"domain\": \"devops\"}'"
    echo ""
    echo -e "${CYAN}${INFO} Development Commands:${NC}"
    echo -e "  ${YELLOW}Start Server:${NC}     python mcp_server/server.py"
    echo -e "  ${YELLOW}Run Tests:${NC}        pytest"
    echo -e "  ${YELLOW}Format Code:${NC}      black . && isort ."
    echo -e "  ${YELLOW}Health Check:${NC}     make health-check"
    echo ""
    echo -e "${CYAN}${GEAR} Cursor Integration:${NC}"
    echo -e "  1. Install MCP extension in Cursor"
    echo -e "  2. Restart Cursor"
    echo -e "  3. Use @infragenius in your chats"
    echo ""
    echo -e "${CYAN}${INFO} Documentation:${NC}"
    echo -e "  ${YELLOW}Local Setup:${NC}      docs/guides/LOCAL_DEVELOPMENT_SETUP.md"
    echo -e "  ${YELLOW}Troubleshooting:${NC}  docs/guides/TROUBLESHOOTING.md"
    echo -e "  ${YELLOW}Development Rules:${NC} docs/guides/DEVELOPMENT_RULES.md"
    echo ""
    echo -e "${CYAN}${INFO} Need Help?${NC}"
    echo -e "  ${YELLOW}GitHub Issues:${NC}    https://github.com/infragenius/infragenius/issues"
    echo -e "  ${YELLOW}Discord:${NC}          https://discord.gg/infragenius"
    echo -e "  ${YELLOW}Documentation:${NC}    https://docs.#"
    echo ""
    echo -e "${GREEN}Happy coding with InfraGenius! 🚀${NC}"
}

# Parse command line arguments
SKIP_SERVER=false
QUIET=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --skip-server)
            SKIP_SERVER=true
            shift
            ;;
        --quiet)
            QUIET=true
            shift
            ;;
        --help)
            echo "InfraGenius Quick Local Setup Script"
            echo ""
            echo "Usage: $0 [options]"
            echo ""
            echo "Options:"
            echo "  --skip-server    Don't start the server after setup"
            echo "  --quiet          Minimal output"
            echo "  --help           Show this help message"
            echo ""
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Main execution
main() {
    if [ "$QUIET" != "true" ]; then
        print_header
    fi
    
    # Check if we're in the right directory
    if [ ! -f "README.md" ] || [ ! -d "mcp_server" ]; then
        print_error "Please run this script from the InfraGenius root directory"
        exit 1
    fi
    
    check_system_requirements
    check_python
    check_ollama
    setup_python_environment
    setup_configuration
    setup_cursor_integration
    run_health_check
    
    if [ "$SKIP_SERVER" != "true" ]; then
        start_server
    fi
    
    if [ "$QUIET" != "true" ]; then
        print_completion
    else
        print_success "Setup completed successfully!"
    fi
}

# Run main function
main "$@"
