# 🚀 Local Development Setup Guide

Complete guide for setting up InfraGenius locally with Ollama and gpt-oss:latest model.

## 📋 Table of Contents

- [Prerequisites](#prerequisites)
- [Quick Setup](#quick-setup)
- [Detailed Setup](#detailed-setup)
- [Cursor Integration](#cursor-integration)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)
- [Development Workflow](#development-workflow)

## 🔧 Prerequisites

### Required Software

| Software | Version | Purpose |
|----------|---------|---------|
| **Python** | 3.9+ (3.11+ recommended) | Core runtime |
| **Ollama** | Latest | Local LLM server |
| **Git** | Latest | Version control |
| **Docker** | 20+ (optional) | Containerization |
| **Node.js** | 18+ (optional) | Documentation |

### System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| **RAM** | 8GB | 16GB+ |
| **CPU** | 4 cores | 8+ cores |
| **Storage** | 20GB free | 50GB+ free |
| **GPU** | None | NVIDIA GPU with 8GB+ VRAM |

---

## 🚀 Quick Setup

### 1. Install Ollama

```bash
# macOS
brew install ollama

# Linux
curl -fsSL https://ollama.ai/install.sh | sh

# Windows (PowerShell)
winget install ollama
```

### 2. Start Ollama Service

```bash
# Start Ollama service
ollama serve

# In a new terminal, pull the required model
ollama pull gpt-oss:latest

# Verify installation
ollama list
```

### 3. Clone and Setup InfraGenius

```bash
# Clone repository
git clone https://github.com/your-username/infragenius.git
cd infragenius

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install
```

### 4. Start InfraGenius

```bash
# Start the MCP server
python mcp_server/server.py

# Or using the CLI
infragenius-server --config mcp_server/config.json
```

### 5. Test Installation

```bash
# Test API endpoint
curl http://localhost:8000/health

# Test AI analysis
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"prompt": "My Kubernetes pods are crashing", "domain": "devops"}'
```

---

## 📖 Detailed Setup

### Step 1: Environment Preparation

#### 1.1 Install Python

```bash
# Check Python version
python --version

# If Python < 3.9, install latest version
# macOS with Homebrew
brew install python@3.11

# Ubuntu/Debian
sudo apt update
sudo apt install python3.11 python3.11-venv python3.11-pip

# Windows - Download from python.org
```

#### 1.2 Install Ollama

**macOS:**
```bash
# Using Homebrew (recommended)
brew install ollama

# Or download from https://ollama.ai
```

**Linux:**
```bash
# Automatic installation
curl -fsSL https://ollama.ai/install.sh | sh

# Manual installation
wget https://ollama.ai/download/ollama-linux-amd64
chmod +x ollama-linux-amd64
sudo mv ollama-linux-amd64 /usr/local/bin/ollama
```

**Windows:**
```powershell
# Using winget
winget install ollama

# Or download installer from https://ollama.ai
```

### Step 2: Ollama Configuration

#### 2.1 Start Ollama Service

```bash
# Start Ollama daemon
ollama serve

# For background service (Linux/macOS)
nohup ollama serve > ollama.log 2>&1 &

# Check if running
ps aux | grep ollama
```

#### 2.2 Download Required Models

```bash
# Pull the main model
ollama pull gpt-oss:latest

# Optional: Pull additional models
ollama pull qwen2.5-coder:latest
ollama pull llama3.1:latest

# List installed models
ollama list

# Test model
ollama run gpt-oss:latest "Hello, how are you?"
```

#### 2.3 Configure Ollama Settings

Create `~/.ollama/config.json`:
```json
{
  "server": {
    "host": "127.0.0.1",
    "port": 11434,
    "timeout": 300,
    "max_connections": 100
  },
  "models": {
    "keep_alive": "5m",
    "num_ctx": 4096,
    "temperature": 0.7,
    "top_p": 0.9
  },
  "performance": {
    "num_gpu": -1,
    "num_thread": 0,
    "use_mlock": true,
    "use_mmap": true
  }
}
```

### Step 3: InfraGenius Setup

#### 3.1 Clone Repository

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/infragenius.git
cd infragenius

# Add upstream remote
git remote add upstream https://github.com/infragenius/infragenius.git

# Verify remotes
git remote -v
```

#### 3.2 Python Environment Setup

```bash
# Create virtual environment
python -m venv venv

# Activate environment
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate   # Windows

# Upgrade pip
pip install --upgrade pip setuptools wheel

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Install in development mode
pip install -e .
```

#### 3.3 Configuration Setup

```bash
# Copy example configuration
cp mcp_server/config.json.example mcp_server/config.json

# Edit configuration
nano mcp_server/config.json
```

**Local Development Configuration** (`mcp_server/config.json`):
```json
{
  "server": {
    "name": "InfraGenius Local Development",
    "host": "127.0.0.1",
    "port": 8000,
    "debug": true,
    "reload": true,
    "log_level": "DEBUG"
  },
  "ollama": {
    "base_url": "http://127.0.0.1:11434",
    "model": "gpt-oss:latest",
    "timeout": 300,
    "max_retries": 3,
    "temperature": 0.7,
    "max_tokens": 4096,
    "stream": true
  },
  "domains": {
    "devops": {
      "enabled": true,
      "expertise_level": "senior",
      "specializations": ["ci_cd", "infrastructure", "automation", "monitoring"]
    },
    "sre": {
      "enabled": true,
      "expertise_level": "principal",
      "specializations": ["reliability", "incident_response", "observability", "slo_management"]
    },
    "cloud": {
      "enabled": true,
      "expertise_level": "architect",
      "platforms": ["aws", "azure", "gcp", "kubernetes"]
    },
    "platform": {
      "enabled": true,
      "expertise_level": "staff",
      "specializations": ["developer_experience", "api_design", "internal_tools"]
    }
  },
  "features": {
    "caching": {
      "enabled": true,
      "type": "memory",
      "ttl": 3600,
      "max_size": 1000
    },
    "rate_limiting": {
      "enabled": false,
      "requests_per_minute": 1000
    },
    "authentication": {
      "enabled": false,
      "type": "none"
    },
    "monitoring": {
      "enabled": true,
      "metrics": true,
      "health_checks": true
    }
  },
  "development": {
    "auto_reload": true,
    "debug_mode": true,
    "verbose_logging": true,
    "cors_enabled": true,
    "cors_origins": ["http://localhost:3000", "http://127.0.0.1:3000"]
  }
}
```

#### 3.4 Environment Variables

Create `.env` file:
```bash
# InfraGenius Local Development Environment

# Server Configuration
INFRAGENIUS_HOST=127.0.0.1
INFRAGENIUS_PORT=8000
INFRAGENIUS_DEBUG=true
INFRAGENIUS_LOG_LEVEL=DEBUG

# Ollama Configuration
OLLAMA_BASE_URL=http://127.0.0.1:11434
OLLAMA_MODEL=gpt-oss:latest
OLLAMA_TIMEOUT=300

# Development Settings
DEVELOPMENT_MODE=true
AUTO_RELOAD=true
CORS_ENABLED=true

# Optional: API Keys for external services
# OPENAI_API_KEY=your_key_here
# ANTHROPIC_API_KEY=your_key_here

# Database (if using)
# DATABASE_URL=sqlite:///./infragenius.db

# Redis (if using)
# REDIS_URL=redis://localhost:6379/0
```

### Step 4: Pre-commit Hooks Setup

```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Test hooks
pre-commit run --all-files

# Update hooks (optional)
pre-commit autoupdate
```

### Step 5: Start Development Server

#### 5.1 Start Ollama (if not running)

```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# If not running, start it
ollama serve
```

#### 5.2 Start InfraGenius Server

```bash
# Method 1: Direct Python
python mcp_server/server.py

# Method 2: Using uvicorn with reload
uvicorn mcp_server.server:app --host 127.0.0.1 --port 8000 --reload

# Method 3: Using the CLI
infragenius-server --config mcp_server/config.json --debug

# Method 4: Using Docker (optional)
docker-compose -f docker/development/docker-compose.yml up
```

#### 5.3 Verify Installation

```bash
# Check health endpoint
curl http://localhost:8000/health

# Check API documentation
open http://localhost:8000/docs

# Test analysis endpoint
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "My Kubernetes pods are crashing with OOMKilled errors",
    "domain": "devops",
    "context": "Production cluster with microservices"
  }'
```

---

## 🎯 Cursor Integration

### MCP Server Integration with Cursor

#### 1. Install Cursor MCP Extension

1. Open Cursor
2. Go to Extensions (Ctrl+Shift+X / Cmd+Shift+X)
3. Search for "MCP" or "Model Context Protocol"
4. Install the official MCP extension

#### 2. Configure Cursor MCP Settings

Create `.cursor/mcp-servers.json`:
```json
{
  "mcpServers": {
    "infragenius": {
      "command": "python",
      "args": ["-m", "mcp_server.cursor_integration"],
      "env": {
        "OLLAMA_BASE_URL": "http://127.0.0.1:11434",
        "OLLAMA_MODEL": "gpt-oss:latest",
        "INFRAGENIUS_CONFIG": "./mcp_server/config.json"
      },
      "description": "InfraGenius DevOps/SRE AI Assistant",
      "capabilities": {
        "tools": true,
        "resources": true,
        "prompts": true
      }
    }
  }
}
```

#### 3. Create Cursor Integration Module

Create `mcp_server/cursor_integration.py`:
```python
#!/usr/bin/env python3
"""
InfraGenius MCP Server for Cursor Integration
"""

import asyncio
import json
import logging
import os
import sys
from typing import Any, Dict, List, Optional

from mcp import ClientSession, StdioServerParameters
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.types import (
    CallToolRequest,
    CallToolResult,
    GetPromptRequest,
    GetPromptResult,
    ListPromptsRequest,
    ListPromptsResult,
    ListResourcesRequest,
    ListResourcesResult,
    ListToolsRequest,
    ListToolsResult,
    Prompt,
    PromptArgument,
    PromptMessage,
    Resource,
    TextContent,
    Tool,
)

from .core.analyzer import InfraGeniusAnalyzer
from .core.config import load_config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize server
server = Server("infragenius")

# Global analyzer instance
analyzer: Optional[InfraGeniusAnalyzer] = None


@server.list_tools()
async def handle_list_tools() -> ListToolsResult:
    """List available tools for Cursor."""
    return ListToolsResult(
        tools=[
            Tool(
                name="analyze_devops_issue",
                description="Analyze DevOps, SRE, Cloud, or Platform Engineering issues",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "prompt": {
                            "type": "string",
                            "description": "The issue or question to analyze"
                        },
                        "domain": {
                            "type": "string",
                            "enum": ["devops", "sre", "cloud", "platform"],
                            "description": "The domain expertise to use"
                        },
                        "context": {
                            "type": "string",
                            "description": "Additional context about your environment"
                        },
                        "urgency": {
                            "type": "string",
                            "enum": ["low", "medium", "high", "critical"],
                            "description": "Issue urgency level"
                        }
                    },
                    "required": ["prompt", "domain"]
                }
            ),
            Tool(
                name="explain_code",
                description="Explain code from DevOps/SRE/Cloud perspective",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "code": {
                            "type": "string",
                            "description": "Code to explain"
                        },
                        "language": {
                            "type": "string",
                            "description": "Programming language"
                        },
                        "focus": {
                            "type": "string",
                            "enum": ["security", "performance", "reliability", "best-practices"],
                            "description": "What to focus on in the explanation"
                        }
                    },
                    "required": ["code"]
                }
            ),
            Tool(
                name="generate_config",
                description="Generate configuration files for DevOps tools",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "tool": {
                            "type": "string",
                            "enum": ["kubernetes", "docker", "terraform", "ansible", "prometheus", "grafana"],
                            "description": "Tool to generate config for"
                        },
                        "requirements": {
                            "type": "string",
                            "description": "Specific requirements for the configuration"
                        },
                        "environment": {
                            "type": "string",
                            "enum": ["development", "staging", "production"],
                            "description": "Target environment"
                        }
                    },
                    "required": ["tool", "requirements"]
                }
            ),
            Tool(
                name="troubleshoot_logs",
                description="Analyze and troubleshoot log files",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "logs": {
                            "type": "string",
                            "description": "Log content to analyze"
                        },
                        "log_type": {
                            "type": "string",
                            "enum": ["application", "system", "kubernetes", "docker", "nginx", "apache"],
                            "description": "Type of logs"
                        },
                        "time_range": {
                            "type": "string",
                            "description": "Time range of the logs"
                        }
                    },
                    "required": ["logs"]
                }
            )
        ]
    )


@server.call_tool()
async def handle_call_tool(request: CallToolRequest) -> CallToolResult:
    """Handle tool calls from Cursor."""
    global analyzer
    
    if analyzer is None:
        return CallToolResult(
            content=[TextContent(
                type="text",
                text="Error: InfraGenius analyzer not initialized"
            )],
            isError=True
        )
    
    try:
        if request.name == "analyze_devops_issue":
            result = await analyzer.analyze(
                prompt=request.arguments["prompt"],
                domain=request.arguments["domain"],
                context=request.arguments.get("context", ""),
                urgency=request.arguments.get("urgency", "medium")
            )
            
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=f"## Analysis Result\n\n{result['analysis']}\n\n## Recommendations\n\n{result['recommendations']}"
                )]
            )
        
        elif request.name == "explain_code":
            result = await analyzer.explain_code(
                code=request.arguments["code"],
                language=request.arguments.get("language", ""),
                focus=request.arguments.get("focus", "best-practices")
            )
            
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=result["explanation"]
                )]
            )
        
        elif request.name == "generate_config":
            result = await analyzer.generate_config(
                tool=request.arguments["tool"],
                requirements=request.arguments["requirements"],
                environment=request.arguments.get("environment", "development")
            )
            
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=f"```yaml\n{result['config']}\n```\n\n## Explanation\n\n{result['explanation']}"
                )]
            )
        
        elif request.name == "troubleshoot_logs":
            result = await analyzer.troubleshoot_logs(
                logs=request.arguments["logs"],
                log_type=request.arguments.get("log_type", "application"),
                time_range=request.arguments.get("time_range", "")
            )
            
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=f"## Log Analysis\n\n{result['analysis']}\n\n## Issues Found\n\n{result['issues']}\n\n## Solutions\n\n{result['solutions']}"
                )]
            )
        
        else:
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=f"Unknown tool: {request.name}"
                )],
                isError=True
            )
    
    except Exception as e:
        logger.error(f"Error handling tool call: {e}")
        return CallToolResult(
            content=[TextContent(
                type="text",
                text=f"Error: {str(e)}"
            )],
            isError=True
        )


@server.list_prompts()
async def handle_list_prompts() -> ListPromptsResult:
    """List available prompts for Cursor."""
    return ListPromptsResult(
        prompts=[
            Prompt(
                name="devops_analysis",
                description="Comprehensive DevOps issue analysis",
                arguments=[
                    PromptArgument(
                        name="issue",
                        description="The DevOps issue to analyze",
                        required=True
                    ),
                    PromptArgument(
                        name="environment",
                        description="Environment context (dev/staging/prod)",
                        required=False
                    )
                ]
            ),
            Prompt(
                name="sre_incident_response",
                description="SRE incident response guidance",
                arguments=[
                    PromptArgument(
                        name="incident",
                        description="Description of the incident",
                        required=True
                    ),
                    PromptArgument(
                        name="severity",
                        description="Incident severity level",
                        required=False
                    )
                ]
            )
        ]
    )


@server.get_prompt()
async def handle_get_prompt(request: GetPromptRequest) -> GetPromptResult:
    """Handle prompt requests from Cursor."""
    if request.name == "devops_analysis":
        issue = request.arguments.get("issue", "")
        environment = request.arguments.get("environment", "production")
        
        return GetPromptResult(
            description="DevOps issue analysis prompt",
            messages=[
                PromptMessage(
                    role="system",
                    content=TextContent(
                        type="text",
                        text=f"""You are an expert DevOps engineer analyzing an issue in a {environment} environment.

Analyze the following issue and provide:
1. Root cause analysis
2. Immediate action items
3. Long-term prevention strategies
4. Monitoring recommendations

Issue: {issue}

Provide a comprehensive analysis with actionable recommendations."""
                    )
                )
            ]
        )
    
    elif request.name == "sre_incident_response":
        incident = request.arguments.get("incident", "")
        severity = request.arguments.get("severity", "medium")
        
        return GetPromptResult(
            description="SRE incident response prompt",
            messages=[
                PromptMessage(
                    role="system",
                    content=TextContent(
                        type="text",
                        text=f"""You are a Senior SRE handling a {severity} severity incident.

Follow the incident response process:
1. Assess and triage
2. Identify immediate actions
3. Communicate status
4. Implement fixes
5. Post-incident review

Incident: {incident}

Provide structured incident response guidance."""
                    )
                )
            ]
        )
    
    else:
        raise ValueError(f"Unknown prompt: {request.name}")


async def main():
    """Main entry point for MCP server."""
    global analyzer
    
    # Load configuration
    config_path = os.getenv("INFRAGENIUS_CONFIG", "mcp_server/config.json")
    config = load_config(config_path)
    
    # Initialize analyzer
    analyzer = InfraGeniusAnalyzer(config)
    await analyzer.initialize()
    
    # Run server
    async with server.run_stdio() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="infragenius",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=None,
                    experimental_capabilities={}
                )
            )
        )


if __name__ == "__main__":
    asyncio.run(main())
```

#### 4. Configure Cursor Settings

Add to Cursor settings (`.cursor/settings.json`):
```json
{
  "mcp.servers": {
    "infragenius": {
      "enabled": true,
      "autoStart": true,
      "timeout": 30000
    }
  },
  "mcp.logging": {
    "enabled": true,
    "level": "info"
  }
}
```

#### 5. Usage in Cursor

1. **Start InfraGenius MCP Server**:
   ```bash
   # Make sure Ollama is running
   ollama serve
   
   # Start InfraGenius MCP server
   python -m mcp_server.cursor_integration
   ```

2. **Use in Cursor**:
   - Open any file in Cursor
   - Use `Cmd/Ctrl + Shift + P` to open command palette
   - Type "MCP: " to see available MCP commands
   - Select "InfraGenius" tools for DevOps analysis

3. **Example Usage**:
   ```
   @infragenius analyze_devops_issue {
     "prompt": "My Kubernetes pods are failing with ImagePullBackOff",
     "domain": "devops",
     "context": "Production cluster on AWS EKS",
     "urgency": "high"
   }
   ```

---

## ⚙️ Configuration

### Local Development Configuration

Create `mcp_server/config.local.json`:
```json
{
  "server": {
    "name": "InfraGenius Local Dev",
    "host": "127.0.0.1",
    "port": 8000,
    "debug": true,
    "reload": true,
    "workers": 1,
    "log_level": "DEBUG"
  },
  "ollama": {
    "base_url": "http://127.0.0.1:11434",
    "model": "gpt-oss:latest",
    "timeout": 300,
    "max_retries": 3,
    "temperature": 0.7,
    "max_tokens": 4096,
    "stream": true,
    "keep_alive": "5m"
  },
  "domains": {
    "devops": {
      "enabled": true,
      "model": "gpt-oss:latest",
      "expertise_level": "senior",
      "specializations": [
        "ci_cd",
        "infrastructure_as_code",
        "automation",
        "monitoring",
        "containerization",
        "orchestration"
      ],
      "context_window": 4096
    },
    "sre": {
      "enabled": true,
      "model": "gpt-oss:latest",
      "expertise_level": "principal",
      "specializations": [
        "reliability_engineering",
        "incident_response",
        "observability",
        "slo_management",
        "capacity_planning",
        "disaster_recovery"
      ],
      "context_window": 4096
    },
    "cloud": {
      "enabled": true,
      "model": "gpt-oss:latest",
      "expertise_level": "architect",
      "platforms": ["aws", "azure", "gcp", "kubernetes", "openshift"],
      "specializations": [
        "architecture_design",
        "security",
        "cost_optimization",
        "migration",
        "multi_cloud"
      ],
      "context_window": 4096
    },
    "platform": {
      "enabled": true,
      "model": "gpt-oss:latest",
      "expertise_level": "staff",
      "specializations": [
        "developer_experience",
        "api_design",
        "internal_tools",
        "platform_engineering",
        "self_service"
      ],
      "context_window": 4096
    }
  },
  "features": {
    "caching": {
      "enabled": true,
      "type": "memory",
      "ttl": 3600,
      "max_size": 1000
    },
    "rate_limiting": {
      "enabled": false
    },
    "authentication": {
      "enabled": false
    },
    "monitoring": {
      "enabled": true,
      "metrics": true,
      "health_checks": true,
      "prometheus": {
        "enabled": false
      }
    },
    "logging": {
      "level": "DEBUG",
      "format": "detailed",
      "file": "logs/infragenius.log",
      "max_size": "10MB",
      "backup_count": 5
    }
  },
  "development": {
    "auto_reload": true,
    "debug_mode": true,
    "verbose_logging": true,
    "cors_enabled": true,
    "cors_origins": [
      "http://localhost:3000",
      "http://127.0.0.1:3000",
      "http://localhost:8080",
      "http://127.0.0.1:8080"
    ],
    "api_docs": {
      "enabled": true,
      "swagger_ui": true,
      "redoc": true
    }
  }
}
```

### Environment-Specific Configurations

Create multiple config files:
- `config.local.json` - Local development
- `config.test.json` - Testing
- `config.staging.json` - Staging environment
- `config.production.json` - Production

---

## 🔧 Development Workflow

### Daily Development Process

1. **Start Development Session**:
   ```bash
   # Activate virtual environment
   source venv/bin/activate
   
   # Start Ollama if not running
   ollama serve
   
   # Pull latest changes
   git pull upstream main
   
   # Install any new dependencies
   pip install -r requirements.txt
   
   # Start InfraGenius
   python mcp_server/server.py --config mcp_server/config.local.json
   ```

2. **Development Testing**:
   ```bash
   # Run unit tests
   pytest tests/unit/ -v
   
   # Run integration tests
   pytest tests/integration/ -v
   
   # Run with coverage
   pytest --cov=mcp_server --cov-report=html
   
   # Run specific test
   pytest tests/unit/test_analyzer.py::test_devops_analysis -v
   ```

3. **Code Quality Checks**:
   ```bash
   # Format code
   black .
   isort .
   
   # Lint code
   flake8 .
   mypy mcp_server/
   
   # Security scan
   bandit -r mcp_server/
   
   # Run all pre-commit hooks
   pre-commit run --all-files
   ```

4. **Git Workflow**:
   ```bash
   # Create feature branch
   git checkout -b feature/your-feature-name
   
   # Make changes and commit
   git add .
   git commit -m "feat: add new feature description"
   
   # Push and create PR
   git push origin feature/your-feature-name
   ```

### Testing Your Changes

1. **Manual Testing**:
   ```bash
   # Test health endpoint
   curl http://localhost:8000/health
   
   # Test analysis
   curl -X POST http://localhost:8000/analyze \
     -H "Content-Type: application/json" \
     -d '{
       "prompt": "Test analysis request",
       "domain": "devops"
     }'
   
   # Test with Cursor integration
   python -m mcp_server.cursor_integration
   ```

2. **Automated Testing**:
   ```bash
   # Run all tests
   make test
   
   # Run specific test suites
   make test-unit
   make test-integration
   make test-performance
   
   # Run tests with different Python versions
   tox
   ```

---

## 🚨 Troubleshooting

### Common Issues and Solutions

#### 1. Ollama Connection Issues

**Problem**: `Connection refused to Ollama server`

**Solutions**:
```bash
# Check if Ollama is running
ps aux | grep ollama

# Check Ollama status
curl http://localhost:11434/api/tags

# Restart Ollama
pkill ollama
ollama serve

# Check Ollama logs
tail -f ~/.ollama/logs/server.log
```

#### 2. Model Download Issues

**Problem**: `gpt-oss:latest model not found`

**Solutions**:
```bash
# List available models
ollama list

# Pull the model
ollama pull gpt-oss:latest

# If model doesn't exist, try alternatives
ollama pull llama3.1:latest
ollama pull qwen2.5-coder:latest

# Update config to use available model
nano mcp_server/config.json
```

#### 3. Python Environment Issues

**Problem**: `ModuleNotFoundError` or dependency conflicts

**Solutions**:
```bash
# Recreate virtual environment
rm -rf venv
python -m venv venv
source venv/bin/activate

# Upgrade pip and setuptools
pip install --upgrade pip setuptools wheel

# Reinstall dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Check for conflicts
pip check
```

#### 4. Port Already in Use

**Problem**: `Port 8000 already in use`

**Solutions**:
```bash
# Find process using port
lsof -i :8000
netstat -tulpn | grep 8000

# Kill process
kill -9 <PID>

# Use different port
python mcp_server/server.py --port 8001
```

#### 5. Cursor Integration Issues

**Problem**: MCP server not connecting to Cursor

**Solutions**:
```bash
# Check MCP server logs
tail -f ~/.cursor/logs/mcp.log

# Verify configuration
cat .cursor/mcp-servers.json

# Restart Cursor MCP server
pkill -f cursor_integration
python -m mcp_server.cursor_integration

# Check Cursor extension status
# Extensions -> MCP -> Check if enabled
```

### Performance Issues

#### 1. Slow Response Times

**Solutions**:
```bash
# Check system resources
htop
nvidia-smi  # If using GPU

# Optimize Ollama settings
nano ~/.ollama/config.json

# Enable GPU acceleration
export OLLAMA_GPU=1

# Increase model keep-alive time
ollama run gpt-oss:latest --keep-alive 10m
```

#### 2. High Memory Usage

**Solutions**:
```bash
# Monitor memory usage
free -h
ps aux --sort=-%mem | head

# Reduce model context window
# Edit config.json -> reduce max_tokens

# Use smaller model for development
ollama pull gpt-oss:7b
```

### Development Issues

#### 1. Pre-commit Hooks Failing

**Solutions**:
```bash
# Update pre-commit hooks
pre-commit autoupdate

# Skip hooks temporarily
git commit --no-verify -m "commit message"

# Fix specific hook issues
black .
isort .
flake8 . --fix
```

#### 2. Tests Failing

**Solutions**:
```bash
# Run tests with verbose output
pytest -v --tb=long

# Run specific failing test
pytest tests/unit/test_analyzer.py::test_specific_function -v -s

# Update test snapshots
pytest --snapshot-update

# Clear pytest cache
pytest --cache-clear
```

### Getting Help

If you encounter issues not covered here:

1. **Check Logs**:
   ```bash
   # InfraGenius logs
   tail -f logs/infragenius.log
   
   # Ollama logs
   tail -f ~/.ollama/logs/server.log
   
   # Cursor logs
   tail -f ~/.cursor/logs/mcp.log
   ```

2. **Community Support**:
   - GitHub Issues: [Create an issue](https://github.com/infragenius/infragenius/issues)
   - Discord: [Join our community](https://discord.gg/infragenius)
   - Discussions: [GitHub Discussions](https://github.com/infragenius/infragenius/discussions)

3. **Debug Mode**:
   ```bash
   # Enable debug logging
   export INFRAGENIUS_LOG_LEVEL=DEBUG
   python mcp_server/server.py --debug
   ```

---

## 📚 Next Steps

After completing the setup:

1. **Explore Examples**: Check `examples/` directory for usage patterns
2. **Read API Docs**: Visit http://localhost:8000/docs
3. **Join Community**: Connect with other developers
4. **Contribute**: See [CONTRIBUTING.md](../../CONTRIBUTING.md)
5. **Advanced Setup**: Explore Docker and Kubernetes deployments

**Happy coding with InfraGenius!** 🚀
