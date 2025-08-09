#!/bin/bash
# Start InfraGenius development environment with local Ollama
# This script ensures Ollama is running locally before starting Docker containers

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_info() {
    echo -e "${BLUE}ℹ️  ${1}${NC}"
}

print_success() {
    echo -e "${GREEN}✅ ${1}${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  ${1}${NC}"
}

print_error() {
    echo -e "${RED}❌ ${1}${NC}"
}

print_header() {
    echo -e "${BLUE}"
    echo "╔═══════════════════════════════════════════════════════════════╗"
    echo "║               InfraGenius Development Setup                   ║"
    echo "║                  with Local Ollama                           ║"
    echo "╚═══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

check_ollama() {
    print_info "Checking local Ollama setup..."
    
    # Check if Ollama is installed
    if ! command -v ollama &> /dev/null; then
        print_error "Ollama not found! Please install Ollama first:"
        echo ""
        echo -e "${YELLOW}Installation commands:${NC}"
        echo -e "  ${BLUE}macOS:${NC}     brew install ollama"
        echo -e "  ${BLUE}Linux:${NC}     curl -fsSL https://ollama.ai/install.sh | sh"
        echo -e "  ${BLUE}Windows:${NC}   winget install ollama"
        echo ""
        echo -e "Or visit: https://ollama.ai"
        exit 1
    fi
    
    print_success "Ollama is installed"
    
    # Check if Ollama service is running
    if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        print_success "Ollama service is running on port 11434"
        
        # List available models
        print_info "Available models:"
        ollama list | head -10
    else
        print_error "Ollama service is not running on port 11434"
        echo ""
        echo -e "${YELLOW}Please start Ollama first:${NC}"
        echo -e "  ${BLUE}ollama serve${NC}"
        echo ""
        echo -e "${YELLOW}Then download a model:${NC}"
        echo -e "  ${BLUE}ollama pull gpt-oss:latest${NC}"
        echo ""
        exit 1
    fi
    
    # Check if gpt-oss model is available
    if ollama list | grep -q "gpt-oss"; then
        print_success "gpt-oss model is available"
    else
        print_warning "gpt-oss model not found"
        print_info "Downloading gpt-oss:latest model..."
        if ollama pull gpt-oss:latest; then
            print_success "Model downloaded successfully"
        else
            print_warning "Failed to download gpt-oss:latest, you can download it manually later"
        fi
    fi
}

check_docker() {
    print_info "Checking Docker setup..."
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker not found! Please install Docker first."
        exit 1
    fi
    
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker daemon is not running. Please start Docker."
        exit 1
    fi
    
    print_success "Docker is ready"
}

start_services() {
    print_info "Starting development services..."
    
    # Navigate to the correct directory
    cd "$(dirname "$0")"
    
    # Start services (without Ollama since it's running locally)
    docker-compose up --build -d postgres redis
    
    print_success "Database and Redis services started"
    
    # Wait for services to be ready
    print_info "Waiting for services to be ready..."
    sleep 5
    
    # Start the main application
    print_info "Starting InfraGenius MCP server..."
    docker-compose up --build mcp-server
}

cleanup() {
    print_info "Cleaning up..."
    cd "$(dirname "$0")"
    docker-compose down
    print_success "Services stopped"
}

# Set trap for cleanup
trap cleanup EXIT

# Main execution
main() {
    print_header
    
    check_ollama
    check_docker
    start_services
}

# Handle command line arguments
case "${1:-}" in
    --stop)
        print_info "Stopping services..."
        cd "$(dirname "$0")"
        docker-compose down
        print_success "Services stopped"
        exit 0
        ;;
    --restart)
        print_info "Restarting services..."
        cd "$(dirname "$0")"
        docker-compose down
        main
        ;;
    --logs)
        cd "$(dirname "$0")"
        docker-compose logs -f
        ;;
    --help)
        echo "InfraGenius Development Environment with Local Ollama"
        echo ""
        echo "Usage: $0 [option]"
        echo ""
        echo "Options:"
        echo "  (no args)  Start development environment"
        echo "  --stop     Stop all services"
        echo "  --restart  Restart all services"
        echo "  --logs     Show service logs"
        echo "  --help     Show this help"
        echo ""
        echo "Prerequisites:"
        echo "  1. Ollama installed and running: ollama serve"
        echo "  2. Model downloaded: ollama pull gpt-oss:latest"
        echo "  3. Docker installed and running"
        echo ""
        exit 0
        ;;
    "")
        main
        ;;
    *)
        print_error "Unknown option: $1"
        echo "Use --help for usage information"
        exit 1
        ;;
esac
