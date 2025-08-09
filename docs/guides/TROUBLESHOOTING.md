# 🔧 Troubleshooting Guide

Complete troubleshooting guide for InfraGenius local development and common issues.

## 📋 Table of Contents

- [Quick Diagnostics](#quick-diagnostics)
- [Ollama Issues](#ollama-issues)
- [Python Environment Issues](#python-environment-issues)
- [Configuration Problems](#configuration-problems)
- [Performance Issues](#performance-issues)
- [Cursor Integration Issues](#cursor-integration-issues)
- [Docker Issues](#docker-issues)
- [Network and Connectivity](#network-and-connectivity)
- [Development Tools Issues](#development-tools-issues)

---

## 🚀 Quick Diagnostics

### System Health Check

Run this comprehensive health check script:

```bash
#!/bin/bash
# health_check.sh - InfraGenius System Health Check

echo "🔍 InfraGenius System Health Check"
echo "=================================="

# Check Python
echo "🐍 Python Version:"
python --version || echo "❌ Python not found"

# Check Ollama
echo -e "\n🤖 Ollama Status:"
if command -v ollama &> /dev/null; then
    echo "✅ Ollama installed"
    if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        echo "✅ Ollama service running"
        echo "📦 Available models:"
        ollama list | head -10
    else
        echo "❌ Ollama service not running"
    fi
else
    echo "❌ Ollama not installed"
fi

# Check InfraGenius
echo -e "\n🧠 InfraGenius Status:"
if [ -f "mcp_server/server.py" ]; then
    echo "✅ InfraGenius code found"
    if [ -f "venv/bin/activate" ] || [ -f "venv/Scripts/activate" ]; then
        echo "✅ Virtual environment found"
    else
        echo "❌ Virtual environment not found"
    fi
else
    echo "❌ InfraGenius code not found"
fi

# Check dependencies
echo -e "\n📦 Dependencies:"
if [ -f "requirements.txt" ]; then
    echo "✅ Requirements file found"
    if command -v pip &> /dev/null; then
        echo "📊 Checking installed packages..."
        pip list | grep -E "(fastapi|ollama|httpx)" || echo "❌ Key packages missing"
    fi
else
    echo "❌ Requirements file not found"
fi

# Check ports
echo -e "\n🌐 Port Status:"
if lsof -i :8000 > /dev/null 2>&1; then
    echo "🔶 Port 8000 in use:"
    lsof -i :8000
else
    echo "✅ Port 8000 available"
fi

if lsof -i :11434 > /dev/null 2>&1; then
    echo "✅ Port 11434 in use (Ollama)"
else
    echo "❌ Port 11434 not in use (Ollama not running)"
fi

# Check disk space
echo -e "\n💾 Disk Space:"
df -h . | tail -1 | awk '{print "Available: " $4 " (" $5 " used)"}'

# Check memory
echo -e "\n🧠 Memory Usage:"
if command -v free &> /dev/null; then
    free -h | grep Mem | awk '{print "Available: " $7 " / " $2}'
elif command -v vm_stat &> /dev/null; then
    # macOS
    vm_stat | head -4
fi

echo -e "\n✅ Health check complete!"
```

### Quick Fix Commands

```bash
# Reset everything
./scripts/reset_development.sh

# Restart services
./scripts/restart_services.sh

# Update dependencies
./scripts/update_dependencies.sh
```

---

## 🤖 Ollama Issues

### Issue: Ollama Not Starting

**Symptoms:**
- `ollama serve` fails to start
- Connection refused errors
- Port 11434 not accessible

**Solutions:**

1. **Check if already running:**
   ```bash
   # Check process
   ps aux | grep ollama
   
   # Check port
   lsof -i :11434
   netstat -tulpn | grep 11434
   ```

2. **Kill existing processes:**
   ```bash
   # Kill all ollama processes
   pkill -f ollama
   
   # Or specific PID
   kill -9 <PID>
   ```

3. **Clean restart:**
   ```bash
   # Clean restart
   pkill -f ollama
   sleep 2
   ollama serve
   ```

4. **Check logs:**
   ```bash
   # Check logs (Linux/macOS)
   tail -f ~/.ollama/logs/server.log
   
   # Or run in foreground for debugging
   ollama serve --debug
   ```

### Issue: Model Not Found

**Symptoms:**
- `model 'gpt-oss:latest' not found`
- Model pull fails
- Empty model list

**Solutions:**

1. **List available models:**
   ```bash
   # List local models
   ollama list
   
   # Search available models
   ollama search gpt-oss
   ```

2. **Pull model manually:**
   ```bash
   # Pull specific model
   ollama pull gpt-oss:latest
   
   # Alternative models
   ollama pull llama3.1:latest
   ollama pull qwen2.5-coder:latest
   
   # Verify download
   ollama list | grep gpt-oss
   ```

3. **Check model size:**
   ```bash
   # Check available disk space
   df -h ~/.ollama
   
   # Large models need 8GB+ free space
   # gpt-oss:latest ≈ 4.1GB
   # llama3.1:latest ≈ 4.7GB
   ```

4. **Use alternative model:**
   ```bash
   # Update config to use available model
   nano mcp_server/config.json
   
   # Change "model": "gpt-oss:latest" to available model
   # Then restart InfraGenius
   ```

### Issue: Slow Model Responses

**Symptoms:**
- Responses take > 30 seconds
- Timeouts occur frequently
- High CPU/memory usage

**Solutions:**

1. **Check system resources:**
   ```bash
   # Monitor resources
   htop
   
   # Check memory usage
   free -h
   
   # Check GPU usage (if available)
   nvidia-smi
   ```

2. **Optimize Ollama settings:**
   ```bash
   # Create Ollama config
   mkdir -p ~/.ollama
   cat > ~/.ollama/config.json << EOF
   {
     "num_ctx": 2048,
     "num_gpu": -1,
     "num_thread": 0,
     "use_mlock": true,
     "use_mmap": true,
     "keep_alive": "5m"
   }
   EOF
   
   # Restart Ollama
   pkill ollama
   ollama serve
   ```

3. **Use smaller model:**
   ```bash
   # Pull smaller model
   ollama pull gpt-oss:7b
   
   # Update config
   sed -i 's/gpt-oss:latest/gpt-oss:7b/g' mcp_server/config.json
   ```

4. **Enable GPU acceleration:**
   ```bash
   # Check GPU support
   nvidia-smi
   
   # Set GPU environment
   export OLLAMA_GPU=1
   export CUDA_VISIBLE_DEVICES=0
   
   # Restart Ollama
   ollama serve
   ```

---

## 🐍 Python Environment Issues

### Issue: ModuleNotFoundError

**Symptoms:**
- `ModuleNotFoundError: No module named 'fastapi'`
- Import errors for dependencies
- Package not found errors

**Solutions:**

1. **Verify virtual environment:**
   ```bash
   # Check if virtual environment is activated
   which python
   echo $VIRTUAL_ENV
   
   # Activate if needed
   source venv/bin/activate  # Linux/macOS
   venv\Scripts\activate     # Windows
   ```

2. **Reinstall dependencies:**
   ```bash
   # Upgrade pip first
   pip install --upgrade pip setuptools wheel
   
   # Install requirements
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   
   # Install in development mode
   pip install -e .
   ```

3. **Check for conflicts:**
   ```bash
   # Check for package conflicts
   pip check
   
   # List installed packages
   pip list
   
   # Show package info
   pip show fastapi
   ```

4. **Recreate environment:**
   ```bash
   # Remove old environment
   rm -rf venv
   
   # Create new environment
   python -m venv venv
   source venv/bin/activate
   
   # Install dependencies
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

### Issue: Python Version Incompatibility

**Symptoms:**
- `Python 3.8 is not supported`
- Syntax errors with new Python features
- Package installation failures

**Solutions:**

1. **Check Python version:**
   ```bash
   # Check version
   python --version
   python3 --version
   
   # Check available versions
   ls /usr/bin/python*
   ```

2. **Install correct Python version:**
   ```bash
   # Ubuntu/Debian
   sudo apt update
   sudo apt install python3.11 python3.11-venv python3.11-pip
   
   # macOS with Homebrew
   brew install python@3.11
   
   # Create environment with specific version
   python3.11 -m venv venv
   ```

3. **Use pyenv for version management:**
   ```bash
   # Install pyenv
   curl https://pyenv.run | bash
   
   # Install Python 3.11
   pyenv install 3.11.7
   pyenv local 3.11.7
   
   # Create environment
   python -m venv venv
   ```

---

## ⚙️ Configuration Problems

### Issue: Invalid Configuration

**Symptoms:**
- `Configuration validation failed`
- Server won't start
- JSON parsing errors

**Solutions:**

1. **Validate JSON syntax:**
   ```bash
   # Check JSON syntax
   python -m json.tool mcp_server/config.json
   
   # Or use jq
   jq . mcp_server/config.json
   ```

2. **Use example configuration:**
   ```bash
   # Copy example config
   cp mcp_server/config.json.example mcp_server/config.json
   
   # Edit as needed
   nano mcp_server/config.json
   ```

3. **Check required fields:**
   ```json
   {
     "server": {
       "host": "127.0.0.1",
       "port": 8000
     },
     "ollama": {
       "base_url": "http://127.0.0.1:11434",
       "model": "gpt-oss:latest"
     }
   }
   ```

4. **Validate configuration:**
   ```bash
   # Test configuration loading
   python -c "
   import json
   with open('mcp_server/config.json') as f:
       config = json.load(f)
   print('✅ Configuration valid')
   print(f'Model: {config[\"ollama\"][\"model\"]}')
   "
   ```

### Issue: Environment Variables Not Loading

**Symptoms:**
- Default values used instead of environment variables
- Configuration not overridden
- Settings not applied

**Solutions:**

1. **Check environment variables:**
   ```bash
   # List all environment variables
   env | grep INFRAGENIUS
   
   # Check specific variables
   echo $INFRAGENIUS_HOST
   echo $OLLAMA_MODEL
   ```

2. **Create .env file:**
   ```bash
   # Create .env file
   cat > .env << EOF
   INFRAGENIUS_HOST=127.0.0.1
   INFRAGENIUS_PORT=8000
   INFRAGENIUS_DEBUG=true
   OLLAMA_BASE_URL=http://127.0.0.1:11434
   OLLAMA_MODEL=gpt-oss:latest
   EOF
   
   # Load environment
   source .env
   ```

3. **Export variables:**
   ```bash
   # Export variables
   export INFRAGENIUS_DEBUG=true
   export OLLAMA_MODEL=gpt-oss:latest
   
   # Verify
   env | grep -E "(INFRAGENIUS|OLLAMA)"
   ```

---

## ⚡ Performance Issues

### Issue: High Memory Usage

**Symptoms:**
- System becomes slow
- Out of memory errors
- Process killed by OOM killer

**Solutions:**

1. **Monitor memory usage:**
   ```bash
   # Monitor system memory
   watch -n 1 free -h
   
   # Monitor process memory
   ps aux --sort=-%mem | head -10
   
   # Check InfraGenius memory usage
   ps aux | grep -E "(python|ollama)"
   ```

2. **Optimize Ollama memory:**
   ```bash
   # Reduce context window
   nano ~/.ollama/config.json
   # Set "num_ctx": 1024 (instead of 4096)
   
   # Reduce keep-alive time
   ollama run gpt-oss:latest --keep-alive 1m
   ```

3. **Use smaller model:**
   ```bash
   # Switch to smaller model
   ollama pull gpt-oss:7b
   
   # Update config
   sed -i 's/gpt-oss:latest/gpt-oss:7b/g' mcp_server/config.json
   ```

4. **Increase swap:**
   ```bash
   # Check swap
   swapon --show
   
   # Create swap file (Linux)
   sudo fallocate -l 4G /swapfile
   sudo chmod 600 /swapfile
   sudo mkswap /swapfile
   sudo swapon /swapfile
   ```

### Issue: Slow Response Times

**Symptoms:**
- API responses take > 10 seconds
- Timeouts occur
- Poor user experience

**Solutions:**

1. **Enable caching:**
   ```json
   // In config.json
   {
     "features": {
       "caching": {
         "enabled": true,
         "type": "memory",
         "ttl": 3600,
         "max_size": 1000
       }
     }
   }
   ```

2. **Optimize model settings:**
   ```json
   {
     "ollama": {
       "temperature": 0.7,
       "max_tokens": 2048,
       "stream": true,
       "keep_alive": "5m"
     }
   }
   ```

3. **Use GPU acceleration:**
   ```bash
   # Install CUDA (NVIDIA)
   # Follow NVIDIA CUDA installation guide
   
   # Set environment variables
   export OLLAMA_GPU=1
   export CUDA_VISIBLE_DEVICES=0
   
   # Restart Ollama
   ollama serve
   ```

---

## 🎯 Cursor Integration Issues

### Issue: MCP Server Not Connecting

**Symptoms:**
- Cursor can't find MCP server
- Connection timeout
- Tools not available in Cursor

**Solutions:**

1. **Check MCP server status:**
   ```bash
   # Test MCP server
   python -m mcp_server.cursor_integration
   
   # Check if process is running
   ps aux | grep cursor_integration
   ```

2. **Verify Cursor configuration:**
   ```bash
   # Check MCP servers config
   cat .cursor/mcp-servers.json
   
   # Verify file exists and is valid JSON
   python -m json.tool .cursor/mcp-servers.json
   ```

3. **Check Cursor logs:**
   ```bash
   # View Cursor MCP logs
   tail -f ~/.cursor/logs/mcp.log
   
   # Or check Cursor console
   # Cursor -> Help -> Toggle Developer Tools -> Console
   ```

4. **Restart MCP server:**
   ```bash
   # Kill existing MCP server
   pkill -f cursor_integration
   
   # Start with debug logging
   PYTHONPATH=. python -m mcp_server.cursor_integration --debug
   ```

### Issue: Tools Not Working in Cursor

**Symptoms:**
- Tools appear but don't execute
- Error messages in Cursor
- Incomplete responses

**Solutions:**

1. **Test tools manually:**
   ```bash
   # Test analysis tool
   curl -X POST http://localhost:8000/analyze \
     -H "Content-Type: application/json" \
     -d '{
       "prompt": "Test analysis",
       "domain": "devops"
     }'
   ```

2. **Check tool configuration:**
   ```python
   # Verify tools are registered
   python -c "
   from mcp_server.cursor_integration import server
   tools = server.list_tools()
   print('Available tools:', [t.name for t in tools])
   "
   ```

3. **Update Cursor extension:**
   ```
   1. Open Cursor
   2. Go to Extensions
   3. Find MCP extension
   4. Update to latest version
   5. Reload Cursor
   ```

---

## 🐳 Docker Issues

### Issue: Docker Build Fails

**Symptoms:**
- `docker build` command fails
- Dependencies not installing
- Image build errors

**Solutions:**

1. **Check Docker daemon:**
   ```bash
   # Check Docker status
   docker info
   
   # Start Docker if not running
   sudo systemctl start docker  # Linux
   # Or start Docker Desktop
   ```

2. **Clear Docker cache:**
   ```bash
   # Clean Docker cache
   docker system prune -a
   
   # Remove old images
   docker rmi $(docker images -q)
   ```

3. **Build with verbose output:**
   ```bash
   # Build with debug output
   docker build --no-cache --progress=plain -t infragenius .
   
   # Check build logs
   docker build -t infragenius . 2>&1 | tee build.log
   ```

4. **Check Dockerfile syntax:**
   ```bash
   # Validate Dockerfile
   docker run --rm -i hadolint/hadolint < Dockerfile
   ```

### Issue: Container Won't Start

**Symptoms:**
- Container exits immediately
- Port binding errors
- Permission issues

**Solutions:**

1. **Check container logs:**
   ```bash
   # View container logs
   docker logs <container_id>
   
   # Follow logs
   docker logs -f infragenius
   ```

2. **Run interactively:**
   ```bash
   # Run container interactively
   docker run -it --rm infragenius /bin/bash
   
   # Check what's happening
   docker run -it --rm infragenius python mcp_server/server.py
   ```

3. **Check port conflicts:**
   ```bash
   # Check if port is in use
   lsof -i :8000
   
   # Use different port
   docker run -p 8001:8000 infragenius
   ```

---

## 🌐 Network and Connectivity

### Issue: Connection Refused

**Symptoms:**
- `Connection refused` errors
- Can't reach localhost:8000
- Network timeouts

**Solutions:**

1. **Check service status:**
   ```bash
   # Check if service is running
   curl -v http://localhost:8000/health
   
   # Check process
   ps aux | grep -E "(python|uvicorn)"
   ```

2. **Verify port binding:**
   ```bash
   # Check what's listening on port 8000
   lsof -i :8000
   netstat -tulpn | grep 8000
   
   # Check all listening ports
   ss -tulpn
   ```

3. **Test with different host:**
   ```bash
   # Try different addresses
   curl http://127.0.0.1:8000/health
   curl http://0.0.0.0:8000/health
   curl http://localhost:8000/health
   ```

4. **Check firewall:**
   ```bash
   # Check firewall status (Linux)
   sudo ufw status
   
   # Allow port if needed
   sudo ufw allow 8000
   ```

### Issue: DNS Resolution Problems

**Symptoms:**
- Can't resolve hostnames
- External API calls fail
- Network requests timeout

**Solutions:**

1. **Test DNS resolution:**
   ```bash
   # Test DNS
   nslookup google.com
   dig google.com
   
   # Check /etc/resolv.conf
   cat /etc/resolv.conf
   ```

2. **Use alternative DNS:**
   ```bash
   # Set DNS servers
   echo "nameserver 8.8.8.8" | sudo tee /etc/resolv.conf
   echo "nameserver 1.1.1.1" | sudo tee -a /etc/resolv.conf
   ```

3. **Check network connectivity:**
   ```bash
   # Test connectivity
   ping -c 4 8.8.8.8
   ping -c 4 google.com
   
   # Test HTTP connectivity
   curl -v http://httpbin.org/get
   ```

---

## 🛠️ Development Tools Issues

### Issue: Pre-commit Hooks Failing

**Symptoms:**
- Commit rejected by pre-commit
- Formatting/linting errors
- Hook execution failures

**Solutions:**

1. **Run hooks manually:**
   ```bash
   # Run all hooks
   pre-commit run --all-files
   
   # Run specific hook
   pre-commit run black --all-files
   pre-commit run flake8 --all-files
   ```

2. **Fix common issues:**
   ```bash
   # Auto-format code
   black .
   isort .
   
   # Fix flake8 issues
   autopep8 --in-place --aggressive --aggressive .
   ```

3. **Update hooks:**
   ```bash
   # Update pre-commit hooks
   pre-commit autoupdate
   
   # Reinstall hooks
   pre-commit uninstall
   pre-commit install
   ```

4. **Skip hooks temporarily:**
   ```bash
   # Skip pre-commit hooks for one commit
   git commit --no-verify -m "commit message"
   
   # Or set environment variable
   SKIP=flake8 git commit -m "commit message"
   ```

### Issue: Tests Failing

**Symptoms:**
- pytest failures
- Import errors in tests
- Assertion errors

**Solutions:**

1. **Run tests with verbose output:**
   ```bash
   # Run with verbose output
   pytest -v --tb=long
   
   # Run specific test
   pytest tests/unit/test_analyzer.py::test_analyze -v -s
   
   # Run with pdb on failure
   pytest --pdb
   ```

2. **Check test environment:**
   ```bash
   # Install test dependencies
   pip install -r requirements-dev.txt
   
   # Check test configuration
   cat pytest.ini
   cat pyproject.toml | grep -A 10 "\[tool.pytest"
   ```

3. **Update test snapshots:**
   ```bash
   # Update snapshots if using pytest-snapshot
   pytest --snapshot-update
   
   # Clear pytest cache
   pytest --cache-clear
   ```

---

## 🆘 Emergency Recovery

### Complete Reset

If everything is broken, use this nuclear option:

```bash
#!/bin/bash
# emergency_reset.sh - Complete InfraGenius Reset

echo "🚨 Emergency Reset - This will delete everything!"
read -p "Are you sure? (type 'yes'): " confirm

if [ "$confirm" != "yes" ]; then
    echo "❌ Reset cancelled"
    exit 1
fi

echo "🧹 Cleaning up..."

# Stop all services
pkill -f ollama
pkill -f python.*server.py
pkill -f uvicorn

# Remove Python environment
rm -rf venv/
rm -rf __pycache__/
rm -rf .pytest_cache/
rm -rf .mypy_cache/
rm -rf *.egg-info/

# Clean Ollama
ollama stop
rm -rf ~/.ollama/models/
rm -rf ~/.ollama/logs/

# Reset git (optional)
git clean -fdx
git reset --hard HEAD

echo "🔄 Reinstalling..."

# Reinstall Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Create new Python environment
python -m venv venv
source venv/bin/activate
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Start services
ollama serve &
sleep 10
ollama pull gpt-oss:latest

# Copy example config
cp mcp_server/config.json.example mcp_server/config.json

echo "✅ Reset complete! Try starting InfraGenius now."
```

### Getting Help

If you're still stuck after trying these solutions:

1. **Create detailed issue:**
   ```bash
   # Collect system info
   ./scripts/collect_debug_info.sh > debug_info.txt
   
   # Create GitHub issue with debug_info.txt attached
   ```

2. **Join community:**
   - Discord: [discord.gg/infragenius](https://discord.gg/infragenius)
   - GitHub Discussions: [github.com/infragenius/infragenius/discussions](https://github.com/infragenius/infragenius/discussions)

3. **Check logs:**
   ```bash
   # Collect all logs
   mkdir -p debug_logs
   cp logs/*.log debug_logs/
   cp ~/.ollama/logs/*.log debug_logs/
   cp ~/.cursor/logs/*.log debug_logs/ 2>/dev/null
   tar -czf debug_logs.tar.gz debug_logs/
   ```

**Remember**: Most issues have simple solutions. Start with the basics (restart services, check configs) before trying complex fixes! 🚀
