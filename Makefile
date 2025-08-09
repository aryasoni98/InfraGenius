# InfraGenius Development Makefile
# Provides convenient commands for development workflow

.PHONY: help install dev-install test lint format clean run docker-build docker-run setup health-check

# Default target
help: ## Show this help message
	@echo "InfraGenius Development Commands"
	@echo "==============================="
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# Installation commands
install: ## Install production dependencies
	pip install --upgrade pip setuptools wheel
	pip install -r requirements.txt

dev-install: ## Install development dependencies
	pip install --upgrade pip setuptools wheel
	pip install -r requirements.txt
	pip install -r requirements-dev.txt
	pip install -e .
	pre-commit install

setup: ## Complete development setup
	@echo "🚀 Setting up InfraGenius development environment..."
	python -m venv venv || echo "Virtual environment already exists"
	@echo "📦 Installing dependencies..."
	$(MAKE) dev-install
	@echo "⚙️ Setting up configuration..."
	cp mcp_server/config.json.example mcp_server/config.json || echo "Config already exists"
	@echo "🤖 Checking Ollama..."
	@command -v ollama >/dev/null 2>&1 || (echo "❌ Ollama not found. Please install: https://ollama.ai" && exit 1)
	@echo "✅ Setup complete! Run 'make run' to start the server."

# Code quality commands
format: ## Format code with black and isort
	black .
	isort .

lint: ## Run linting checks
	black --check .
	isort --check-only .
	flake8 .
	mypy mcp_server/

security: ## Run security checks
	bandit -r mcp_server/
	safety check

quality: format lint security ## Run all code quality checks

# Testing commands
test: ## Run all tests
	pytest

test-unit: ## Run unit tests only
	pytest tests/unit/ -v

test-integration: ## Run integration tests only
	pytest tests/integration/ -v

test-performance: ## Run performance tests
	pytest tests/performance/ -v --benchmark-only

test-coverage: ## Run tests with coverage report
	pytest --cov=mcp_server --cov-report=html --cov-report=term

test-watch: ## Run tests in watch mode
	pytest-watch

# Development server commands
run: ## Start development server
	@echo "🚀 Starting InfraGenius development server..."
	@echo "📊 Health check: http://localhost:8000/health"
	@echo "📚 API docs: http://localhost:8000/docs"
	python mcp_server/server.py

run-debug: ## Start server in debug mode
	INFRAGENIUS_DEBUG=true INFRAGENIUS_LOG_LEVEL=DEBUG python mcp_server/server.py

run-reload: ## Start server with auto-reload
	uvicorn mcp_server.server:app --host 127.0.0.1 --port 8000 --reload

run-production: ## Start server in production mode
	uvicorn mcp_server.server:app --host 0.0.0.0 --port 8000 --workers 4

# Ollama commands
ollama-start: ## Start Ollama service
	@echo "🤖 Starting Ollama service..."
	ollama serve &
	@echo "⏳ Waiting for Ollama to start..."
	@sleep 5
	@echo "✅ Ollama started"

ollama-pull: ## Pull required Ollama models
	@echo "📦 Pulling gpt-oss:latest model..."
	ollama pull gpt-oss:latest
	@echo "📦 Pulling alternative models..."
	ollama pull llama3.1:latest || echo "⚠️ Could not pull llama3.1:latest"
	ollama pull qwen2.5-coder:latest || echo "⚠️ Could not pull qwen2.5-coder:latest"

ollama-list: ## List installed Ollama models
	ollama list

ollama-setup: ollama-start ollama-pull ## Complete Ollama setup

# Health and diagnostics
health-check: ## Run comprehensive health check
	@echo "🔍 InfraGenius Health Check"
	@echo "=========================="
	@echo "🐍 Python version:"
	@python --version
	@echo ""
	@echo "📦 Virtual environment:"
	@which python
	@echo ""
	@echo "🤖 Ollama status:"
	@curl -s http://localhost:11434/api/tags >/dev/null && echo "✅ Ollama running" || echo "❌ Ollama not running"
	@echo ""
	@echo "📊 Available models:"
	@ollama list 2>/dev/null || echo "❌ Could not list models"
	@echo ""
	@echo "🌐 Port status:"
	@lsof -i :8000 >/dev/null && echo "🔶 Port 8000 in use" || echo "✅ Port 8000 available"
	@lsof -i :11434 >/dev/null && echo "✅ Port 11434 in use (Ollama)" || echo "❌ Port 11434 not in use"

diagnose: ## Run diagnostic checks
	@echo "🔧 Running diagnostics..."
	python -c "import sys; print(f'Python: {sys.version}')"
	python -c "import mcp_server; print('✅ InfraGenius importable')" 2>/dev/null || echo "❌ Import error"
	python -c "import json; json.load(open('mcp_server/config.json')); print('✅ Config valid')" 2>/dev/null || echo "❌ Config invalid"

# Docker commands (with local Ollama)
docker-build: ## Build Docker image
	docker build -t infragenius:latest -f docker/development/Dockerfile .

docker-dev: ## Run Docker development environment with local Ollama
	@echo "🐳 Starting Docker development environment..."
	@echo "📋 Prerequisites: Ollama must be running locally (ollama serve)"
	./docker/development/start-with-local-ollama.sh

docker-dev-bg: ## Run Docker development environment in background
	docker-compose -f docker/development/docker-compose.yml up -d

docker-logs: ## Show Docker logs
	docker-compose -f docker/development/docker-compose.yml logs -f

docker-stop: ## Stop Docker containers
	docker-compose -f docker/development/docker-compose.yml down

docker-restart: ## Restart Docker development environment
	./docker/development/start-with-local-ollama.sh --restart

docker-clean: ## Clean Docker images and containers
	docker-compose -f docker/development/docker-compose.yml down -v
	docker system prune -f

docker-check: ## Check Docker setup and local Ollama
	@echo "🔍 Checking Docker and Ollama setup..."
	@docker --version || echo "❌ Docker not installed"
	@docker info > /dev/null 2>&1 && echo "✅ Docker daemon running" || echo "❌ Docker daemon not running"
	@command -v ollama >/dev/null 2>&1 && echo "✅ Ollama installed" || echo "❌ Ollama not installed"
	@curl -s http://localhost:11434/api/tags >/dev/null 2>&1 && echo "✅ Ollama running on :11434" || echo "❌ Ollama not running on :11434"

# Database commands (if using)
db-migrate: ## Run database migrations
	alembic upgrade head

db-reset: ## Reset database
	alembic downgrade base
	alembic upgrade head

# Documentation commands
docs-build: ## Build documentation
	mkdocs build

docs-serve: ## Serve documentation locally
	mkdocs serve

docs-deploy: ## Deploy documentation
	mkdocs gh-deploy

# Maintenance commands
clean: ## Clean up generated files
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	rm -rf htmlcov/
	rm -rf dist/
	rm -rf build/

clean-all: clean ## Clean everything including virtual environment
	rm -rf venv/
	rm -rf logs/
	rm -rf .coverage

reset: clean-all setup ## Complete reset and setup

# Git and release commands
pre-commit: ## Run pre-commit hooks on all files
	pre-commit run --all-files

commit: pre-commit ## Run pre-commit checks before committing
	@echo "✅ Pre-commit checks passed. Ready to commit."

release-patch: ## Create patch release
	bump2version patch
	git push
	git push --tags

release-minor: ## Create minor release
	bump2version minor
	git push
	git push --tags

release-major: ## Create major release
	bump2version major
	git push
	git push --tags

# Performance and profiling
profile: ## Profile the application
	py-spy record -o profile.svg --duration 30 --pid $(shell pgrep -f "python.*server.py")

benchmark: ## Run performance benchmarks
	pytest tests/performance/ --benchmark-only --benchmark-json=benchmark.json

load-test: ## Run load tests
	locust -f tests/performance/locustfile.py --host=http://localhost:8000

# Cursor integration commands
cursor-setup: ## Setup Cursor MCP integration
	@echo "🎯 Setting up Cursor MCP integration..."
	mkdir -p .cursor
	@echo "Creating MCP server configuration..."
	@cat > .cursor/mcp-servers.json << 'EOF'
	{
	  "mcpServers": {
	    "infragenius": {
	      "command": "python",
	      "args": ["-m", "mcp_server.cursor_integration"],
	      "env": {
	        "OLLAMA_BASE_URL": "http://127.0.0.1:11434",
	        "OLLAMA_MODEL": "gpt-oss:latest",
	        "INFRAGENIUS_CONFIG": "./mcp_server/config.json"
	      }
	    }
	  }
	}
	EOF
	@echo "✅ Cursor MCP configuration created at .cursor/mcp-servers.json"

cursor-test: ## Test Cursor MCP integration
	python -m mcp_server.cursor_integration --test

# Utility commands
logs: ## Show server logs
	tail -f logs/infragenius.log

logs-follow: ## Follow all logs
	tail -f logs/*.log

env-info: ## Show environment information
	@echo "Environment Information:"
	@echo "======================="
	@echo "OS: $(shell uname -s)"
	@echo "Architecture: $(shell uname -m)"
	@echo "Python: $(shell python --version)"
	@echo "Pip: $(shell pip --version)"
	@echo "Virtual env: $$VIRTUAL_ENV"
	@echo "Working dir: $(shell pwd)"
	@echo "Git branch: $(shell git branch --show-current 2>/dev/null || echo 'Not a git repo')"

# Development workflow shortcuts
dev: setup ollama-setup ## Complete development setup
	@echo "🎉 Development environment ready!"
	@echo "🚀 Run 'make run' to start the server"
	@echo "📊 Run 'make health-check' to verify everything works"

quick-start: ## Quick start for new developers
	@echo "🚀 InfraGenius Quick Start"
	@echo "========================="
	@echo "1. Setting up environment..."
	$(MAKE) setup
	@echo "2. Setting up Ollama..."
	$(MAKE) ollama-setup
	@echo "3. Running health check..."
	$(MAKE) health-check
	@echo "4. Starting server..."
	$(MAKE) run

# CI/CD simulation
ci: quality test ## Simulate CI pipeline
	@echo "✅ CI pipeline completed successfully"

# Advanced commands
shell: ## Open development shell
	@echo "🐚 Opening InfraGenius development shell..."
	@echo "Available commands: make help"
	@PYTHONPATH=. bash

debug: ## Start debugging session
	@echo "🐛 Starting debug session..."
	python -m pdb mcp_server/server.py

monitor: ## Monitor system resources
	@echo "📊 Monitoring system resources (Ctrl+C to stop)..."
	watch -n 1 'echo "=== Memory ===" && free -h && echo "=== CPU ===" && top -bn1 | head -5 && echo "=== Disk ===" && df -h . && echo "=== Processes ===" && ps aux | grep -E "(python|ollama)" | head -5'

# Help with colors
help-color: ## Show colorized help
	@echo "\033[36mInfraGenius Development Commands\033[0m"
	@echo "\033[36m===============================\033[0m"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[32m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# Default environment variables
export PYTHONPATH := .
export INFRAGENIUS_ENV := development
