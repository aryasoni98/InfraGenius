# Local Production Environment Setup Guide

## 🎯 Overview

This guide will help you set up your local macOS system as a **production-level environment** for the DevOps/SRE MCP Server. You'll have a complete production stack running locally with:

- ✅ **Kubernetes cluster** (k3d) with production configuration
- ✅ **PostgreSQL & Redis** databases
- ✅ **Monitoring stack** (Prometheus + Grafana)
- ✅ **Auto-scaling** and load balancing
- ✅ **Production Docker images** and configurations
- ✅ **Security** and authentication systems
- ✅ **Performance optimization** and caching

## 🚀 Quick Start

### **Option 1: Automated Setup (Recommended)**
```bash
# Run the automated setup script
./local_production_setup.sh setup

# This will:
# - Install all required tools
# - Set up Kubernetes cluster
# - Deploy databases
# - Build and deploy your MCP server
# - Set up monitoring
# - Configure ingress and DNS
```

### **Option 2: Manual Step-by-Step**
Follow the detailed steps below for full control over the setup process.

## 📋 Prerequisites

### **System Requirements**
- **macOS** (optimized for Apple Silicon, but works on Intel)
- **16GB+ RAM** (recommended for optimal performance)
- **20GB+ free disk space**
- **Docker Desktop** installed and running
- **Homebrew** package manager

### **Resource Allocation**
```bash
# Check your system resources
system_profiler SPHardwareDataType | grep "Memory:"
df -h .  # Check disk space

# Recommended Docker settings:
# - Memory: 8GB minimum, 12GB recommended
# - CPUs: 4+ cores
# - Disk: 60GB+ for images and data
```

## 🛠️ Manual Setup Steps

### **Step 1: Install Required Tools**
```bash
# Install Homebrew (if not already installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install required tools
brew install docker kubectl helm k3d redis postgresql@15 jq yq

# Start Docker Desktop
open -a Docker
```

### **Step 2: Set Up Local Kubernetes Cluster**
```bash
# Create production-like k3d cluster
k3d cluster create mcp-production-local \
    --agents 2 \
    --port "8080:80@loadbalancer" \
    --port "8443:443@loadbalancer" \
    --k3s-arg "--disable=traefik@server:0" \
    --registry-create "mcp-registry.localhost:5000" \
    --volume "/tmp/k3d-mcp-storage:/var/lib/rancher/k3s/storage@all"

# Verify cluster is running
kubectl cluster-info
kubectl get nodes
```

### **Step 3: Set Up Local Databases**
```bash
# Start PostgreSQL
brew services start postgresql@15

# Create database and user
psql postgres -c "CREATE DATABASE mcpserver;"
psql postgres -c "CREATE USER mcpuser WITH PASSWORD 'mcppass123';"
psql postgres -c "GRANT ALL PRIVILEGES ON DATABASE mcpserver TO mcpuser;"

# Start Redis
brew services start redis

# Test connections
psql "postgresql://mcpuser:mcppass123@localhost:5432/mcpserver" -c "SELECT version();"
redis-cli ping
```

### **Step 4: Build Production Docker Image**
```bash
# Use production requirements
cp requirements.production.txt requirements.txt

# Build production image
docker build -f Dockerfile.production -t mcp-server:production .

# Tag and push to local registry
docker tag mcp-server:production localhost:5000/mcp-server:production
docker push localhost:5000/mcp-server:production
```

### **Step 5: Deploy to Kubernetes**
```bash
# Apply all production manifests
kubectl apply -f k8s/local-production/

# Wait for deployments
kubectl wait --for=condition=available --timeout=300s deployment/mcp-server -n mcp-production

# Check status
kubectl get pods -n mcp-production
kubectl get services -n mcp-production
```

### **Step 6: Set Up Monitoring**
```bash
# Install Prometheus and Grafana
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

helm install prometheus prometheus-community/kube-prometheus-stack \
    --namespace monitoring \
    --create-namespace \
    --set grafana.adminPassword=admin123 \
    --set prometheus.prometheusSpec.retention=7d

# Wait for monitoring stack
kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=grafana -n monitoring --timeout=300s
```

### **Step 7: Set Up Ingress and DNS**
```bash
# Install NGINX Ingress Controller
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.2/deploy/static/provider/cloud/deploy.yaml

# Add local DNS entries
echo "127.0.0.1 mcp-server.local" | sudo tee -a /etc/hosts
echo "127.0.0.1 grafana.local" | sudo tee -a /etc/hosts

# Set up port forwarding
kubectl port-forward -n mcp-production svc/mcp-server-service 8080:80 &
kubectl port-forward -n monitoring svc/prometheus-grafana 3000:80 &
```

## 🎛️ Production Configuration

### **Environment Variables**
```bash
# Set production environment variables
export ENVIRONMENT=local-production
export CONFIG_PATH=/config/config.json
export DATABASE_URL=postgresql://mcpuser:mcppass123@host.k3d.internal:5432/mcpserver
export REDIS_URL=redis://host.k3d.internal:6379/0
export JWT_SECRET=your-super-secret-jwt-key-change-in-production
```

### **Configuration Files**
The setup uses production-ready configurations:

- **`config.production.json`**: Complete production configuration
- **`requirements.production.txt`**: All production dependencies
- **`k8s/local-production/`**: Production Kubernetes manifests

### **Key Production Features Enabled**
```yaml
Features:
  - Auto-scaling (HPA): 2-10 replicas based on CPU/memory
  - Health checks: Liveness, readiness, and startup probes
  - Resource limits: CPU and memory constraints
  - Security: JWT authentication, rate limiting
  - Monitoring: Prometheus metrics, Grafana dashboards
  - Caching: Multi-level Redis and in-memory caching
  - Performance: Connection pooling, async processing
  - Observability: Structured logging, distributed tracing
```

## 📊 Accessing Services

### **Primary Services**
```bash
# MCP Server API
curl http://localhost:8080/health
curl http://localhost:8080/ready
curl http://localhost:8080/metrics

# API endpoints
curl -X POST http://localhost:8080/analyze \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Analyze this DevOps pipeline failure", "domain": "devops"}'
```

### **Monitoring & Observability**
```bash
# Grafana Dashboard (admin/admin123)
open http://localhost:3000

# Prometheus Metrics
open http://localhost:9090

# Kubernetes Dashboard
kubectl proxy &
open http://localhost:8001/api/v1/namespaces/kubernetes-dashboard/services/https:kubernetes-dashboard:/proxy/
```

### **Database Access**
```bash
# PostgreSQL
psql "postgresql://mcpuser:mcppass123@localhost:5432/mcpserver"

# Redis CLI
redis-cli

# View database from pods
kubectl exec -it -n mcp-production deployment/mcp-server -- env
```

## 🧪 Testing Production Features

### **Load Testing**
```bash
# Install Apache Bench
brew install apache-bench

# Test API performance
ab -n 1000 -c 10 http://localhost:8080/health

# Test with authentication
ab -n 100 -c 5 -H "Authorization: Bearer YOUR_JWT_TOKEN" \
   -T "application/json" \
   -p test_payload.json \
   http://localhost:8080/analyze
```

### **Auto-Scaling Test**
```bash
# Generate load to trigger auto-scaling
kubectl run -i --tty load-generator --rm --image=busybox --restart=Never -- \
  /bin/sh -c "while true; do wget -q -O- http://mcp-server-service.mcp-production/health; done"

# Watch pods scale up
kubectl get hpa -n mcp-production -w
kubectl get pods -n mcp-production -w
```

### **Monitoring Alerts**
```bash
# View Prometheus targets
curl http://localhost:9090/api/v1/targets

# Check alert rules
curl http://localhost:9090/api/v1/rules

# View active alerts
curl http://localhost:9090/api/v1/alerts
```

## 🔧 Production Operations

### **Deployment Updates**
```bash
# Update the application
docker build -f Dockerfile.production -t mcp-server:production .
docker tag mcp-server:production localhost:5000/mcp-server:production
docker push localhost:5000/mcp-server:production

# Rolling update
kubectl rollout restart deployment/mcp-server -n mcp-production
kubectl rollout status deployment/mcp-server -n mcp-production
```

### **Scaling Operations**
```bash
# Manual scaling
kubectl scale deployment mcp-server --replicas=5 -n mcp-production

# Update HPA settings
kubectl patch hpa mcp-server-hpa -n mcp-production -p '{"spec":{"maxReplicas":15}}'

# Check resource usage
kubectl top pods -n mcp-production
kubectl top nodes
```

### **Debugging and Troubleshooting**
```bash
# View logs
kubectl logs -f deployment/mcp-server -n mcp-production

# Debug pod issues
kubectl describe pod -l app=mcp-server -n mcp-production

# Check events
kubectl get events -n mcp-production --sort-by=.metadata.creationTimestamp

# Execute into pod
kubectl exec -it deployment/mcp-server -n mcp-production -- /bin/bash
```

### **Performance Monitoring**
```bash
# View metrics
curl http://localhost:8080/metrics

# Check database performance
psql "postgresql://mcpuser:mcppass123@localhost:5432/mcpserver" \
  -c "SELECT * FROM pg_stat_activity;"

# Redis performance
redis-cli info stats
redis-cli info memory
```

## 📈 Production Metrics & KPIs

### **Application Metrics**
- **Response Time**: < 2 seconds average
- **Throughput**: 100+ requests/second
- **Error Rate**: < 0.1%
- **Uptime**: > 99.9%
- **Cache Hit Rate**: > 80%

### **Infrastructure Metrics**
- **CPU Usage**: < 70% average
- **Memory Usage**: < 80% average
- **Disk I/O**: Monitored and alerted
- **Network Latency**: < 100ms internal

### **Business Metrics**
- **API Usage**: Tracked per user/tier
- **Feature Adoption**: Domain-specific usage
- **User Satisfaction**: Response quality metrics

## 🚨 Troubleshooting Guide

### **Common Issues**

#### **Pods Not Starting**
```bash
# Check pod status
kubectl get pods -n mcp-production
kubectl describe pod <pod-name> -n mcp-production

# Common fixes:
# 1. Check resource limits
# 2. Verify image pull
# 3. Check configuration
# 4. Review secrets and configmaps
```

#### **Database Connection Issues**
```bash
# Test database connectivity
kubectl exec -it deployment/mcp-server -n mcp-production -- \
  psql "postgresql://mcpuser:mcppass123@host.k3d.internal:5432/mcpserver" -c "SELECT 1;"

# Check database logs
brew services list | grep postgresql
tail -f /usr/local/var/log/postgresql@15.log
```

#### **Performance Issues**
```bash
# Check resource usage
kubectl top pods -n mcp-production
kubectl top nodes

# Review HPA status
kubectl get hpa -n mcp-production
kubectl describe hpa mcp-server-hpa -n mcp-production

# Check for memory leaks
kubectl exec deployment/mcp-server -n mcp-production -- ps aux
```

### **Performance Optimization**
```bash
# Enable performance profiling
kubectl patch deployment mcp-server -n mcp-production -p '
{
  "spec": {
    "template": {
      "spec": {
        "containers": [
          {
            "name": "mcp-server",
            "env": [
              {
                "name": "PROFILING_ENABLED",
                "value": "true"
              }
            ]
          }
        ]
      }
    }
  }
}'

# View profiling data
curl http://localhost:8080/debug/pprof/
```

## 🧹 Cleanup

### **Complete Cleanup**
```bash
# Use the automated cleanup
./local_production_setup.sh cleanup

# Or manual cleanup:
kubectl delete namespace mcp-production
helm uninstall prometheus -n monitoring
kubectl delete namespace monitoring
k3d cluster delete mcp-production-local
brew services stop postgresql@15
brew services stop redis
docker system prune -a
```

### **Partial Cleanup**
```bash
# Just restart the application
kubectl rollout restart deployment/mcp-server -n mcp-production

# Reset databases
psql postgres -c "DROP DATABASE mcpserver;"
psql postgres -c "CREATE DATABASE mcpserver;"
redis-cli FLUSHALL
```

## 🎉 Success Validation

Your local production environment is ready when:

✅ **All pods are running**: `kubectl get pods -n mcp-production`  
✅ **Health checks pass**: `curl http://localhost:8080/health`  
✅ **Metrics are available**: `curl http://localhost:8080/metrics`  
✅ **Grafana dashboards load**: `http://localhost:3000`  
✅ **Auto-scaling works**: Load test triggers scaling  
✅ **Database connections work**: No connection errors in logs  
✅ **API responses are fast**: < 2 second response times  

## 🚀 Next Steps

With your local production environment running:

1. **Test all API endpoints** with realistic payloads
2. **Validate performance** under load
3. **Test failure scenarios** (database down, high load, etc.)
4. **Optimize configurations** based on metrics
5. **Prepare for cloud deployment** using the same configurations

Your local system is now running a **production-grade DevOps/SRE MCP Server** with enterprise-level features and monitoring! 🎉
