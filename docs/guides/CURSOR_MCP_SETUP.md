# 🎯 Cursor MCP Setup Guide

Complete guide for integrating InfraGenius as an MCP server with Cursor IDE.

## 📋 Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Step-by-Step Setup](#step-by-step-setup)
- [Configuration Examples](#configuration-examples)
- [Usage Guide](#usage-guide)
- [Troubleshooting](#troubleshooting)
- [Advanced Configuration](#advanced-configuration)

---

## 🎯 Overview

InfraGenius integrates with Cursor as an **MCP (Model Context Protocol) server**, providing specialized DevOps, SRE, Cloud, and Platform Engineering expertise directly in your IDE.

### **What You Get:**
- 🔧 **DevOps Expert** - CI/CD, deployment, automation guidance
- 🚨 **SRE Specialist** - Incident response, reliability engineering
- ☁️ **Cloud Architect** - Architecture review, cost optimization
- ⚙️ **Config Generator** - K8s, Docker, Terraform configurations
- 📋 **Log Analyzer** - Error investigation and debugging
- 🏗️ **Platform Engineer** - Developer experience optimization

---

## 🔧 Prerequisites

### **Required Software**
- ✅ **Cursor IDE** - Latest version with MCP support
- ✅ **Ollama** - Running locally with models
- ✅ **Python 3.9+** - For InfraGenius
- ✅ **InfraGenius** - Cloned and set up locally

### **Required Models**
Download at least one of these models in Ollama:
```bash
# Recommended (best performance)
ollama pull gpt-oss:latest

# Alternatives
ollama pull gpt-oss:20b
ollama pull llama3.1:latest
ollama pull qwen2.5-coder:latest
```

### **Verify Prerequisites**
```bash
# Check Ollama
curl http://localhost:11434/api/tags

# Check InfraGenius
cd /path/to/InfraGenius
source venv/bin/activate
python -c "import mcp_server.cursor_integration; print('✅ Ready')"
```

---

## 🚀 Step-by-Step Setup

### **Step 1: Install MCP Dependency**

```bash
cd /path/to/InfraGenius
source venv/bin/activate
pip install mcp
```

### **Step 2: Locate Your mcp.json File**

The file location depends on your OS:

| OS | Location |
|----|----------|
| **macOS** | `~/.cursor/mcp.json` |
| **Linux** | `~/.cursor/mcp.json` |
| **Windows** | `%APPDATA%\Cursor\mcp.json` |

### **Step 3: Update mcp.json Configuration**

#### **Option A: New Configuration (if file doesn't exist)**

Create `~/.cursor/mcp.json`:
```json
{
  "mcpServers": {
    "infragenius": {
      "command": "/FULL/PATH/TO/InfraGenius/venv/bin/python",
      "args": [
        "-m", "mcp_server.cursor_integration"
      ],
      "cwd": "/FULL/PATH/TO/InfraGenius",
      "env": {
        "OLLAMA_BASE_URL": "http://localhost:11434",
        "OLLAMA_MODEL": "gpt-oss:latest",
        "PYTHONPATH": "/FULL/PATH/TO/InfraGenius"
      }
    }
  }
}
```

#### **Option B: Add to Existing Configuration**

If you already have MCP servers, add InfraGenius to the existing `mcpServers` object:

```json
{
  "mcpServers": {
    "existing-server": {
      "command": "existing-command",
      "args": ["existing-args"]
    },
    "infragenius": {
      "command": "/FULL/PATH/TO/InfraGenius/venv/bin/python",
      "args": ["-m", "mcp_server.cursor_integration"],
      "cwd": "/FULL/PATH/TO/InfraGenius",
      "env": {
        "OLLAMA_BASE_URL": "http://localhost:11434",
        "OLLAMA_MODEL": "gpt-oss:latest"
      }
    }
  }
}
```

### **Step 4: Update Paths**

Replace `/FULL/PATH/TO/InfraGenius` with your actual paths:

```bash
# Find your full path
cd /path/to/InfraGenius
pwd
# Copy this output to use in mcp.json
```

**Example paths:**
- macOS: `/Users/john/Documents/CodeBase/InfraGenius`
- Linux: `/home/john/projects/InfraGenius`
- Windows: `C:\Users\john\projects\InfraGenius`

### **Step 5: Restart Cursor**

**Important**: Completely close and reopen Cursor for changes to take effect.

### **Step 6: Verify Setup**

1. Open any file in Cursor
2. Start a new chat
3. Type `@infragenius` - you should see it in the autocomplete
4. Try a test command:
   ```
   @infragenius analyze_devops_issue {
     "prompt": "Test connection",
     "urgency": "low"
   }
   ```

---

## ⚙️ Configuration Examples

### **Example 1: Basic Configuration**
```json
{
  "mcpServers": {
    "infragenius": {
      "command": "/Users/john/InfraGenius/venv/bin/python",
      "args": ["-m", "mcp_server.cursor_integration"],
      "cwd": "/Users/john/InfraGenius"
    }
  }
}
```

### **Example 2: With Specific Model**
```json
{
  "mcpServers": {
    "infragenius": {
      "command": "/Users/john/InfraGenius/venv/bin/python",
      "args": ["-m", "mcp_server.cursor_integration"],
      "cwd": "/Users/john/InfraGenius",
      "env": {
        "OLLAMA_MODEL": "gpt-oss:20b"
      }
    }
  }
}
```

### **Example 3: Multiple MCP Servers**
```json
{
  "mcpServers": {
    "qwen3-32b": {
      "command": "ollama-mcp-server",
      "args": ["qwen3:32b"],
      "env": {
        "OLLAMA_HOST": "http://localhost:11434"
      }
    },
    "gpt-oss-20b": {
      "command": "ollama-mcp-server",
      "args": ["gpt-oss:20b"],
      "env": {
        "OLLAMA_HOST": "http://localhost:11434"
      }
    },
    "infragenius": {
      "command": "/Users/john/InfraGenius/venv/bin/python",
      "args": ["-m", "mcp_server.cursor_integration"],
      "cwd": "/Users/john/InfraGenius",
      "env": {
        "OLLAMA_MODEL": "gpt-oss:20b"
      }
    }
  }
}
```

### **Example 4: Custom Ollama Host**
```json
{
  "mcpServers": {
    "infragenius": {
      "command": "/Users/john/InfraGenius/venv/bin/python",
      "args": ["-m", "mcp_server.cursor_integration"],
      "cwd": "/Users/john/InfraGenius",
      "env": {
        "OLLAMA_BASE_URL": "http://192.168.1.100:11434",
        "OLLAMA_MODEL": "gpt-oss:latest"
      }
    }
  }
}
```

---

## 🎯 Usage Guide

### **Available Tools**

| Tool Name | Purpose | Example Use Case |
|-----------|---------|------------------|
| `analyze_devops_issue` | DevOps troubleshooting | CI/CD pipeline failures |
| `analyze_sre_incident` | Incident response | Service outages, alerts |
| `review_cloud_architecture` | Architecture analysis | Cost optimization |
| `generate_config` | Config file generation | Kubernetes manifests |
| `explain_logs` | Log analysis | Error debugging |
| `platform_engineering_advice` | Platform guidance | Developer experience |

### **Basic Usage Patterns**

#### **1. DevOps Issue Analysis**
```javascript
@infragenius analyze_devops_issue {
  "prompt": "Docker build failing with permission denied error",
  "context": "Ubuntu 20.04, Jenkins CI pipeline",
  "urgency": "medium"
}
```

#### **2. SRE Incident Response**
```javascript
@infragenius analyze_sre_incident {
  "incident": "API response time increased from 200ms to 2s",
  "severity": "high",
  "affected_services": "user-api, payment-service"
}
```

#### **3. Cloud Architecture Review**
```javascript
@infragenius review_cloud_architecture {
  "architecture": "Microservices on EKS with RDS PostgreSQL and ElastiCache",
  "cloud_provider": "aws",
  "focus_area": "security"
}
```

#### **4. Configuration Generation**
```javascript
@infragenius generate_config {
  "tool": "kubernetes",
  "requirements": "Redis cluster with 3 replicas, persistence, and monitoring",
  "environment": "production"
}
```

#### **5. Log Analysis**
```javascript
@infragenius explain_logs {
  "logs": "2024-01-15 10:30:45 ERROR [pool-1-thread-1] c.e.s.DatabaseService - Connection pool exhausted",
  "log_type": "application"
}
```

#### **6. Platform Engineering**
```javascript
@infragenius platform_engineering_advice {
  "challenge": "Reduce developer setup time from 2 days to 2 hours",
  "team_size": "25 developers",
  "tech_stack": "React, Node.js, PostgreSQL, Kubernetes"
}
```

### **Advanced Usage Tips**

#### **Chaining Tools**
```javascript
// First analyze the issue
@infragenius analyze_devops_issue {
  "prompt": "Kubernetes pods randomly restarting"
}

// Then generate a monitoring config
@infragenius generate_config {
  "tool": "prometheus",
  "requirements": "Monitor pod restarts and resource usage"
}
```

#### **Context-Rich Queries**
```javascript
@infragenius analyze_sre_incident {
  "incident": "Database queries timing out",
  "severity": "critical",
  "affected_services": "All user-facing services",
  "context": "Started after deployment 2 hours ago, affects 60% of requests, connection pool showing 95% utilization"
}
```

---

## 🔧 Troubleshooting

### **Common Issues**

#### **1. `@infragenius` doesn't appear in autocomplete**

**Possible causes:**
- Cursor wasn't restarted after configuration
- Wrong paths in mcp.json
- Python virtual environment not found

**Solutions:**
```bash
# Check paths are correct
ls -la /path/to/InfraGenius/venv/bin/python

# Test integration manually
cd /path/to/InfraGenius
source venv/bin/activate
python -m mcp_server.cursor_integration

# Restart Cursor completely
```

#### **2. "Module not found" errors**

**Possible causes:**
- MCP library not installed
- Python path issues
- Virtual environment not activated

**Solutions:**
```bash
# Install MCP in virtual environment
cd /path/to/InfraGenius
source venv/bin/activate
pip install mcp

# Verify installation
python -c "import mcp; print('MCP installed')"
```

#### **3. Ollama connection errors**

**Possible causes:**
- Ollama not running
- Wrong Ollama URL
- Model not available

**Solutions:**
```bash
# Check Ollama status
curl http://localhost:11434/api/tags

# Start Ollama if needed
ollama serve

# Check model availability
ollama list | grep gpt-oss
```

#### **4. Tool execution fails**

**Possible causes:**
- Invalid JSON in tool parameters
- Missing required parameters
- Model response errors

**Solutions:**
- Check JSON syntax in tool calls
- Ensure all required parameters are provided
- Check Cursor's developer console for errors

### **Debug Commands**

```bash
# Test MCP integration
cd /path/to/InfraGenius
source venv/bin/activate
python -c "
import asyncio
from mcp_server.cursor_integration import server
print('✅ MCP server can be imported')
"

# Test Ollama connection
curl -X POST http://localhost:11434/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-oss:latest",
    "prompt": "Hello",
    "stream": false
  }'

# Check Python environment
which python
python --version
pip list | grep mcp
```

### **Getting Help**

If you're still having issues:

1. **Check Cursor logs**: Look in Cursor's developer console
2. **Verify setup**: Run the debug commands above
3. **Create issue**: [GitHub Issues](https://github.com/infragenius/infragenius/issues)
4. **Join Discord**: [Community Support](https://discord.gg/infragenius)

---

## 🚀 Advanced Configuration

### **Custom Model Selection**

Use different models for different scenarios:
```json
{
  "mcpServers": {
    "infragenius-fast": {
      "command": "/path/to/InfraGenius/venv/bin/python",
      "args": ["-m", "mcp_server.cursor_integration"],
      "cwd": "/path/to/InfraGenius",
      "env": {
        "OLLAMA_MODEL": "gpt-oss:7b"
      }
    },
    "infragenius-powerful": {
      "command": "/path/to/InfraGenius/venv/bin/python",
      "args": ["-m", "mcp_server.cursor_integration"],
      "cwd": "/path/to/InfraGenius", 
      "env": {
        "OLLAMA_MODEL": "gpt-oss:20b"
      }
    }
  }
}
```

### **Remote Ollama Setup**

Connect to Ollama running on a different machine:
```json
{
  "mcpServers": {
    "infragenius": {
      "command": "/path/to/InfraGenius/venv/bin/python",
      "args": ["-m", "mcp_server.cursor_integration"],
      "cwd": "/path/to/InfraGenius",
      "env": {
        "OLLAMA_BASE_URL": "http://192.168.1.100:11434",
        "OLLAMA_MODEL": "gpt-oss:latest"
      }
    }
  }
}
```

### **Development vs Production**

Different configurations for different environments:
```json
{
  "mcpServers": {
    "infragenius-dev": {
      "command": "/path/to/InfraGenius/venv/bin/python",
      "args": ["-m", "mcp_server.cursor_integration"],
      "cwd": "/path/to/InfraGenius",
      "env": {
        "OLLAMA_MODEL": "gpt-oss:7b",
        "DEBUG": "true"
      }
    }
  }
}
```

---

## 🎉 Success Checklist

After setup, you should have:

- ✅ `@infragenius` appears in Cursor autocomplete
- ✅ Tools are available when typing `@infragenius`
- ✅ Test queries return helpful responses
- ✅ No errors in Cursor's developer console
- ✅ Ollama is running with required models

**You're ready to use InfraGenius as your AI DevOps/SRE assistant in Cursor!** 🚀

---

*For more information, see the main [README.md](../../README.md) and [Local Development Setup](LOCAL_DEVELOPMENT_SETUP.md).*
