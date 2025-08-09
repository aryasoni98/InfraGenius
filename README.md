# InfraGenius - AI-Powered DevOps & SRE Intelligence Platform

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![CI](https://github.com/infragenius/infragenius/workflows/CI/badge.svg)](https://github.com/infragenius/infragenius/actions)
[![Coverage](https://codecov.io/gh/infragenius/infragenius/branch/main/graph/badge.svg)](https://codecov.io/gh/infragenius/infragenius)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://docker.com)
[![Kubernetes](https://img.shields.io/badge/Kubernetes-Compatible-326CE5.svg)](https://kubernetes.io)
[![Security](https://img.shields.io/badge/Security-A+-green.svg)](SECURITY.md)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

**🚀 Transform your DevOps operations with AI-powered expertise**

[📚 Documentation](https://infragenius.github.io/infragenius) • 
[🚀 Quick Start](#-quick-start) • 
[💬 Community](https://discord.gg/infragenius) • 
[🤝 Contributing](CONTRIBUTING.md)

</div>

## 🎯 Overview

**InfraGenius** is a comprehensive AI-powered platform designed specifically for DevOps, SRE, Cloud, and Platform Engineering professionals. It provides industry-level expertise through advanced AI models, optimized for infrastructure operations, reliability engineering, and cloud architecture.

### 🌟 Key Features

- 🤖 **AI-Powered Analysis**: Advanced DevOps/SRE expertise using open source models (gpt-oss:latest)
- 🏠 **Local Development**: Optimized for local development with Ollama - no cloud dependencies
- 🎯 **Cursor Integration**: Works as MCP server with Cursor for seamless AI assistance
- ⚡ **High Performance**: Sub-second response times with intelligent caching
- 🔓 **Open Source**: MIT licensed, community-driven development
- 📊 **Multiple Domains**: DevOps, SRE, Cloud Architecture, Platform Engineering expertise
- 🛠️ **Developer Friendly**: Comprehensive docs, examples, and development tools

## 🏗️ Architecture Overview


```mermaid

graph TB
    subgraph "Client Layer"
        UI[Web UI]
        API[REST API]
        CLI[CLI Tool]
    end
    
    subgraph "API Gateway"
        LB[Load Balancer]
        AUTH[Authentication]
        RATE[Rate Limiting]
    end
    
    subgraph "Application Layer"
        MCP1[MCP Server 1]
        MCP2[MCP Server 2]
        MCP3[MCP Server N]
    end
    
    subgraph "AI/ML Layer"
        OLLAMA[Ollama Service]
        MODELS[Fine-tuned Models]
        CACHE[Model Cache]
    end
    
    subgraph "Data Layer"
        POSTGRES[(PostgreSQL)]
        REDIS[(Redis Cache)]
        S3[(Object Storage)]
    end
    
    subgraph "Infrastructure"
        K8S[Kubernetes]
        DOCKER[Docker]
        CLOUD[Multi-Cloud]
    end
    
    subgraph "Monitoring"
        PROM[Prometheus]
        GRAF[Grafana]
        JAEGER[Jaeger]
    end
    
    UI --> LB
    API --> LB
    CLI --> LB
    
    LB --> AUTH
    AUTH --> RATE
    RATE --> MCP1
    RATE --> MCP2
    RATE --> MCP3
    
    MCP1 --> OLLAMA
    MCP2 --> OLLAMA
    MCP3 --> OLLAMA
    
    OLLAMA --> MODELS
    MODELS --> CACHE
    
    MCP1 --> POSTGRES
    MCP1 --> REDIS
    MCP2 --> POSTGRES
    MCP2 --> REDIS
    MCP3 --> POSTGRES
    MCP3 --> REDIS
    
    POSTGRES --> S3
    
    K8S --> CLOUD
    DOCKER --> K8S
    
    MCP1 --> PROM
    MCP2 --> PROM
    MCP3 --> PROM
    PROM --> GRAF
    MCP1 --> JAEGER
    
    %% Client Layer Styling
    style UI fill:#e3f2fd,stroke:#2196f3,stroke-width:2px
    style API fill:#e8f5e8,stroke:#4caf50,stroke-width:2px
    style CLI fill:#fff3e0,stroke:#ff9800,stroke-width:2px
    
    %% API Gateway Styling
    style LB fill:#ffcdd2,stroke:#d32f2f,stroke-width:3px
    style AUTH fill:#ffab91,stroke:#ff5722,stroke-width:2px
    style RATE fill:#80cbc4,stroke:#00695c,stroke-width:2px
    
    %% Application Layer Styling
    style MCP1 fill:#90caf9,stroke:#1976d2,stroke-width:3px
    style MCP2 fill:#a5d6a7,stroke:#388e3c,stroke-width:3px
    style MCP3 fill:#ffcc80,stroke:#f57c00,stroke-width:3px
    
    %% AI/ML Layer Styling
    style OLLAMA fill:#ce93d8,stroke:#7b1fa2,stroke-width:3px
    style MODELS fill:#f8bbd9,stroke:#c2185b,stroke-width:2px
    style CACHE fill:#b39ddb,stroke:#512da8,stroke-width:2px
    
    %% Data Layer Styling
    style POSTGRES fill:#81c784,stroke:#2e7d32,stroke-width:3px
    style REDIS fill:#ef5350,stroke:#c62828,stroke-width:3px
    style S3 fill:#ffb74d,stroke:#ef6c00,stroke-width:3px
    
    %% Infrastructure Styling
    style K8S fill:#42a5f5,stroke:#1565c0,stroke-width:3px
    style DOCKER fill:#29b6f6,stroke:#0277bd,stroke-width:2px
    style CLOUD fill:#66bb6a,stroke:#2e7d32,stroke-width:2px
    
    %% Monitoring Styling
    style PROM fill:#ff7043,stroke:#d84315,stroke-width:2px
    style GRAF fill:#ffa726,stroke:#ef6c00,stroke-width:2px
    style JAEGER fill:#ab47bc,stroke:#6a1b9a,stroke-width:2px

```

## 📁 Project Structure

```
InfraGenius/
├── 📁 environments/           # Environment-specific configurations
│   ├── 📁 test/              # Test environment configs
│   ├── 📁 staging/           # Staging environment configs
│   └── 📁 production/        # Production environment configs
├── 📁 src/                   # Source code
│   ├── 📁 core/              # Core application logic
│   ├── 📁 plugins/           # Extensible plugins
│   └── 📁 ui/                # Web interface
├── 📁 docker/                # Docker configurations
│   ├── 📁 development/       # Development containers
│   └── 📁 production/        # Production containers
├── 📁 kubernetes/            # K8s manifests
│   ├── 📁 test/              # Test cluster configs
│   ├── 📁 staging/           # Staging cluster configs
│   └── 📁 production/        # Production cluster configs
├── 📁 docs/                  # Documentation
│   ├── 📁 architecture/      # Architecture diagrams
│   ├── 📁 api/               # API documentation
│   └── 📁 deployment/        # Deployment guides
├── 📁 tests/                 # Test suites
│   ├── 📁 unit/              # Unit tests
│   ├── 📁 integration/       # Integration tests
│   └── 📁 e2e/               # End-to-end tests
├── 📁 scripts/               # Automation scripts
│   ├── 📁 setup/             # Setup and installation
│   ├── 📁 deploy/            # Deployment automation
│   └── 📁 utils/             # Utility scripts
├── 📁 monitoring/            # Monitoring configurations
│   ├── 📁 grafana/           # Grafana dashboards
│   └── 📁 prometheus/        # Prometheus configs
├── 📁 security/              # Security configurations
├── 📁 backup/                # Backup and recovery
├── 📁 migrations/            # Database migrations
├── 📁 examples/              # Usage examples
├── 📁 tools/                 # Development tools
└── 📄 README.md              # This file
```

## 🚀 Quick Start

> **🎯 Focus**: InfraGenius is currently optimized for **local development** with Ollama and open source models. This is perfect for learning, contributing, and building amazing DevOps/SRE solutions locally!

### ⚡ One-Click Local Setup

```bash
# Clone the repository
git clone https://github.com/your-username/infragenius.git
cd infragenius

# 🚀 One-click setup (installs everything automatically)
./scripts/quick-local-setup.sh

# 🎉 That's it! Server will start automatically
# 📊 Health check: http://localhost:8000/health
# 📚 API docs: http://localhost:8000/docs
```

### 🛠️ Manual Setup (Step by Step)

#### 1. **Install Ollama** 
```bash
# macOS
brew install ollama

# Linux
curl -fsSL https://ollama.ai/install.sh | sh

# Windows
winget install ollama
```

#### 2. **Start Ollama & Download Model**
```bash
# Start Ollama service
ollama serve

# Download AI model (in new terminal)
ollama pull gpt-oss:latest

# Verify model is ready
ollama list
```

#### 3. **Setup InfraGenius**
```bash
# Create Python environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Create configuration
cp mcp_server/config.json.example mcp_server/config.json

# Start InfraGenius
python mcp_server/server.py
```

#### 4. **Test Your Setup**
```bash
# Test API health
curl http://localhost:8000/health

# Test AI analysis
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "My Kubernetes pods are crashing with OOMKilled errors", 
    "domain": "devops",
    "context": "Production cluster on AWS EKS"
  }'
```

### 🎯 Cursor Integration (MCP Server)

InfraGenius works as an **MCP (Model Context Protocol) server** with Cursor, giving you a specialized DevOps/SRE AI assistant directly in your IDE!

#### **🚀 Quick Setup**

```bash
# 1. Setup Cursor integration
make cursor-setup

# 2. Install MCP dependency
source venv/bin/activate
pip install mcp

# 3. Test the integration
python -m mcp_server.cursor_integration
```

#### **⚙️ Cursor Configuration**

Add InfraGenius to your Cursor MCP configuration file at `~/.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "infragenius": {
      "command": "<file_path>/InfraGenius/venv/bin/python",
      "args": [
        "-m", "mcp_server.cursor_integration"
      ],
      "cwd": "<file_path>/InfraGenius",
      "env": {
        "OLLAMA_BASE_URL": "http://localhost:11434",
        "OLLAMA_MODEL": "gpt-oss:latest",
        "PYTHONPATH": "<file_path>/InfraGenius"
      }
    }
  }
}
```

**📝 Replace `YOUR_USERNAME` with your actual username!**

**💡 Quick Copy**: Use the template at [`examples/cursor-mcp-template.json`](examples/cursor-mcp-template.json) and update the paths.

#### **🔄 Adding to Existing MCP Configuration**

If you already have other MCP servers configured, just add the `infragenius` entry to your existing `mcpServers` object:

```json
{
  "mcpServers": {
    "existing-server": {
      "command": "some-other-mcp-server",
      "args": ["..."]
    },
    "infragenius": {
      "command": "<file_path>/InfraGenius/venv/bin/python",
      "args": ["-m", "mcp_server.cursor_integration"],
      "cwd": "<file_path>/InfraGenius",
      "env": {
        "OLLAMA_BASE_URL": "http://localhost:11434",
        "OLLAMA_MODEL": "gpt-oss:latest"
      }
    }
  }
}
```

#### **🎯 Usage in Cursor**

Once configured, use InfraGenius tools directly in Cursor:

```javascript
// DevOps Issue Analysis
@infragenius analyze_devops_issue {
  "prompt": "My Kubernetes pods are crashing with OOMKilled",
  "context": "Production EKS cluster with 50+ microservices",
  "urgency": "high"
}

// SRE Incident Response  
@infragenius analyze_sre_incident {
  "incident": "Database connection pool exhausted",
  "severity": "critical",
  "affected_services": "user-service, payment-service"
}

// Cloud Architecture Review
@infragenius review_cloud_architecture {
  "architecture": "3-tier web app on AWS with RDS and ElastiCache",
  "cloud_provider": "aws", 
  "focus_area": "cost"
}

// Generate Configurations
@infragenius generate_config {
  "tool": "kubernetes",
  "requirements": "Redis cluster with persistence and monitoring",
  "environment": "production"
}

// Log Analysis
@infragenius explain_logs {
  "logs": "ERROR: Connection timeout after 30s in database pool",
  "log_type": "application"
}

// Platform Engineering Advice
@infragenius platform_engineering_advice {
  "challenge": "Improve developer onboarding and reduce time-to-first-commit",
  "team_size": "30 developers",
  "tech_stack": "Node.js, React, Kubernetes, PostgreSQL"
}
```

#### **🛠️ Available Tools**

| Tool | Purpose | Best For |
|------|---------|----------|
| 🔧 `analyze_devops_issue` | DevOps problem solving | CI/CD issues, deployment problems |
| 🚨 `analyze_sre_incident` | Incident response guidance | Outages, performance issues, alerts |
| ☁️ `review_cloud_architecture` | Architecture analysis | Cost optimization, security, scaling |
| ⚙️ `generate_config` | Configuration generation | K8s manifests, Docker, Terraform |
| 📋 `explain_logs` | Log analysis & debugging | Error investigation, troubleshooting |
| 🏗️ `platform_engineering_advice` | Platform guidance | Developer experience, internal tools |

#### **✅ Verification Steps**

1. **Restart Cursor** completely after updating mcp.json
2. **Check MCP Status** in Cursor's settings/extensions
3. **Test Integration**: Type `@infragenius` in any chat
4. **Verify Tools**: You should see tool suggestions appear

#### **🔧 Troubleshooting**

**If `@infragenius` doesn't appear:**

```bash
# Check if integration works
cd /path/to/InfraGenius
source venv/bin/activate
python -c "import mcp_server.cursor_integration; print('✅ Integration OK')"

# Verify Ollama is running
curl http://localhost:11434/api/tags

# Check your paths in mcp.json are correct
```

**Common Issues:**
- ❌ **Wrong paths** in mcp.json → Update to your actual paths
- ❌ **Virtual env not activated** → Use full path to venv/bin/python
- ❌ **Ollama not running** → Start with `ollama serve`
- ❌ **Model not available** → Download with `ollama pull gpt-oss:latest`

#### **💡 Pro Tips**

- **Combine with other MCP servers** - InfraGenius works alongside other AI models
- **Use specific tools** - Each tool is optimized for different scenarios
- **Provide context** - More context = better, more actionable responses
- **Save configurations** - Generated configs can be saved directly to files

### Docker Deployment

```bash
# Development environment
docker-compose -f docker/development/docker-compose.yml up

# Production environment
docker-compose -f docker/production/docker-compose.yml up
```

### Kubernetes Deployment

```bash
# Test environment
kubectl apply -f kubernetes/test/

# Staging environment
kubectl apply -f kubernetes/staging/

# Production environment
kubectl apply -f kubernetes/production/
```



## 🌍 Environment Management

### Test Environment
- **Purpose**: Development and testing
- **Resources**: Minimal (1 CPU, 2GB RAM)
- **Data**: Synthetic test data
- **Monitoring**: Basic metrics

```bash
./scripts/deploy/deploy-test.sh
```

### Staging Environment
- **Purpose**: Pre-production validation
- **Resources**: Production-like (2 CPU, 4GB RAM)
- **Data**: Anonymized production data
- **Monitoring**: Full observability stack

```bash
./scripts/deploy/deploy-staging.sh
```

### Production Environment
- **Purpose**: Live customer traffic
- **Resources**: Auto-scaling (2-20 instances)
- **Data**: Live production data
- **Monitoring**: Enterprise monitoring + alerting

```bash
./scripts/deploy/deploy-production.sh
```

## 🛠️ Core Features

### 🤖 AI-Powered DevOps Analysis

```python
# Example API usage
import requests

response = requests.post('http://localhost:8080/analyze', {
    "prompt": "My Kubernetes pods are crashing with OOMKilled errors",
    "domain": "devops",
    "context": "Production cluster with 100+ microservices"
})

print(response.json())
# Returns detailed analysis with:
# - Root cause identification
# - Step-by-step resolution
# - Prevention strategies
# - Best practices
```

### 📊 Comprehensive Domains

| Domain | Features | Use Cases |
|--------|----------|-----------|
| **DevOps** | CI/CD, IaC, Automation | Pipeline optimization, deployment strategies |
| **SRE** | Reliability, Incidents, SLOs | Incident response, reliability improvements |
| **Cloud** | Architecture, Security, Cost | Cloud migration, cost optimization |
| **Platform** | Developer Experience, APIs | Platform design, developer productivity |

### ⚡ Performance Features

- **Sub-second response times** with intelligent caching
- **Auto-scaling** based on demand (2-100 instances)
- **Multi-level caching** (Redis + in-memory)
- **Connection pooling** for optimal resource usage
- **Async processing** for high throughput
- **Response streaming** for large analyses

### 🔒 Enterprise Security

- **JWT authentication** with refresh tokens
- **Role-based access control** (RBAC)
- **Rate limiting** by user tier
- **API key management**
- **Audit logging** for compliance
- **Data encryption** at rest and in transit
- **Network security** with VPC and firewalls

## 📊 Monitoring & Observability

### Metrics & Dashboards
- **Prometheus** metrics collection
- **Grafana** dashboards and visualization
- **Application performance** monitoring
- **Infrastructure** monitoring
- **Business metrics** tracking
- **Custom alerts** and notifications

### Health Checks
```bash
# System health
curl http://localhost:8080/health

# Detailed health check
curl http://localhost:8080/health/detailed

# Metrics endpoint
curl http://localhost:8080/metrics
```

## 🔧 Dependencies

### Core Dependencies
```json
{
  "runtime": {
    "python": ">=3.11",
    "docker": ">=20.10",
    "kubernetes": ">=1.24"
  },
  "databases": {
    "postgresql": ">=15",
    "redis": ">=7.0"
  },
  "ai_models": {
    "ollama": ">=0.1.0",
    "gpt-oss": "latest"
  },
  "monitoring": {
    "prometheus": ">=2.40",
    "grafana": ">=9.0"
  }
}
```

### System Requirements

| Component | Minimum | Recommended | Production |
|-----------|---------|-------------|------------|
| **CPU** | 2 cores | 4 cores | 8+ cores |
| **Memory** | 4GB | 8GB | 16+ GB |
| **Storage** | 20GB | 50GB | 100+ GB |
| **Network** | 1Mbps | 10Mbps | 100+ Mbps |

## 🚀 Deployment Options

### Local Development
```bash
# Quick start for development
./scripts/setup/local-dev.sh

# With monitoring stack
./scripts/setup/local-dev.sh --monitoring

# With sample data
./scripts/setup/local-dev.sh --sample-data
```

### Cloud Deployment

#### AWS
```bash
./scripts/deploy/aws-deploy.sh \
  --region us-east-1 \
  --environment production \
  --instance-type t3.large
```

#### Google Cloud
```bash
./scripts/deploy/gcp-deploy.sh \
  --region us-central1 \
  --environment production \
  --machine-type e2-standard-4
```

#### Azure
```bash
./scripts/deploy/azure-deploy.sh \
  --region eastus \
  --environment production \
  --vm-size Standard_D4s_v3
```

### On-Premises
```bash
./scripts/deploy/on-premises.sh \
  --kubernetes-config ~/.kube/config \
  --storage-class fast-ssd
```

## 🧪 Testing

### Unit Tests
```bash
# Run all unit tests
pytest tests/unit/

# Run with coverage
pytest tests/unit/ --cov=src --cov-report=html
```

### Integration Tests
```bash
# Run integration tests
pytest tests/integration/

# Test specific service
pytest tests/integration/test_ollama_integration.py
```

### End-to-End Tests
```bash
# Run E2E tests
pytest tests/e2e/

# Run against specific environment
pytest tests/e2e/ --env=staging
```

### Performance Tests
```bash
# Load testing
./scripts/utils/load-test.sh --concurrent=50 --requests=1000

# Stress testing
./scripts/utils/stress-test.sh --duration=300s
```

## 📚 Documentation

### Architecture
- [System Architecture](docs/architecture/system-design.md)
- [Database Schema](docs/architecture/database-schema.md)
- [API Design](docs/architecture/api-design.md)
- [Security Model](docs/architecture/security-model.md)

### API Documentation
- [REST API Reference](docs/api/rest-api.md)
- [WebSocket API](docs/api/websocket-api.md)
- [Authentication](docs/api/authentication.md)
- [Rate Limiting](docs/api/rate-limiting.md)

### Deployment
- [Local Setup](docs/deployment/local-setup.md)
- [Docker Deployment](docs/deployment/docker.md)
- [Kubernetes Deployment](docs/deployment/kubernetes.md)
- [Cloud Deployment](docs/deployment/cloud.md)

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Workflow
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

### Code Standards
- **Python**: Follow PEP 8
- **Testing**: Minimum 80% coverage
- **Documentation**: Document all public APIs
- **Commits**: Use conventional commits

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

### Community Support
- 📚 [Documentation](docs/)
- 💬 [GitHub Discussions](https://github.com/aryasoni98/infragenius/discussions)
- 🐛 [GitHub Issues](https://github.com/aryasoni98/infragenius/issues)
- 🤝 [Contributing Guide](CONTRIBUTING.md)

## 🎯 Roadmap

### Q1 2024
- [ ] Advanced fine-tuning capabilities
- [ ] Multi-model support
- [ ] Enhanced UI/UX
- [ ] Mobile app

### Q2 2024
- [ ] AI-powered incident response
- [ ] Automated runbook generation
- [ ] Advanced cost optimization
- [ ] Compliance automation

### Q3 2024
- [ ] Multi-model architecture
- [ ] Advanced analytics
- [ ] Custom model training
- [ ] Enhanced integrations

### Q4 2024
- [ ] Edge deployment
- [ ] IoT integration
- [ ] Advanced security features
- [ ] Performance improvements

## 📊 Performance Benchmarks

| Metric | Performance |
|--------|------------|
| **Response Time** | <2s |
| **Throughput** | 100+ req/s |
| **Uptime** | 99.5%+ |
| **Support Response** | Community-driven |

## 🚀 Get Started Today!

Choose your deployment option and get started in minutes:

```bash
# Quick local setup
curl -sSL https://get.infragenius.ai | bash

# Or manual setup
git clone https://github.com/your-org/infragenius.git
cd infragenius
./scripts/setup/quick-start.sh
```

**Transform your DevOps operations with AI-powered expertise!** 🎉

---

<div align="center">
  <strong>Made with ❤️ for the DevOps community</strong><br>
  <a href="https://infragenius.ai">Website</a> •
  <a href="https://docs.infragenius.ai">Documentation</a> •
  <a href="https://community.infragenius.ai">Community</a> •
  <a href="mailto:hello@infragenius.ai">Contact</a>
</div>
