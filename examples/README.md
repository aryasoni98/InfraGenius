# InfraGenius Examples

This directory contains various examples demonstrating how to use InfraGenius for different use cases.

## 📁 Directory Structure

### **Configuration Templates**
- **`cursor-mcp-template.json`** - Cursor MCP configuration template

### **Usage Examples**
- **`basic/`** - Simple examples to get started
- **`advanced/`** - Complex use cases and configurations  
- **`integrations/`** - Integration examples with other tools

## 🎯 Cursor MCP Setup

### **Quick Template**
Use the [`cursor-mcp-template.json`](cursor-mcp-template.json) template:

1. Copy the template to `~/.cursor/mcp.json`
2. Replace `REPLACE_WITH_FULL_PATH_TO_INFRAGENIUS` with your actual path
3. Restart Cursor
4. Use `@infragenius` in your chats!

## 🚀 Quick Start Examples

### Basic Usage
```python
# See basic/simple_analysis.py
from infragenius import InfraGenius

client = InfraGenius()
result = client.analyze("My pods are crashing with OOMKilled errors")
print(result.recommendations)
```

### Advanced Configuration
```python
# See advanced/custom_config.py
from infragenius import InfraGenius, Config

config = Config(
    model="gpt-oss-devops:latest",
    domain="sre",
    expertise_level="principal"
)

client = InfraGenius(config=config)
```

### Integration Examples
- **Kubernetes** - `integrations/kubernetes_monitoring.py`
- **Prometheus** - `integrations/prometheus_alerts.py`
- **CI/CD** - `integrations/github_actions.py`

## 📚 Documentation

For complete documentation, visit: https://docs.infragenius.ai

## 🤝 Contributing

Found an issue or want to add an example? See our [Contributing Guide](../CONTRIBUTING.md).
